import os
from functools import lru_cache

from chatbot.ml.lstm_dataset import PAD_TOKEN
from chatbot.ml.lstm_model import CartLSTMRecommender, torch
from chatbot.models import ProductDocument, UserBehavior


def default_model_path():
    model_dir = os.getenv("AI_MODEL_DIR", os.path.join(os.getcwd(), "models"))
    return os.path.join(model_dir, "cart_lstm_recommender.pt")


@lru_cache(maxsize=1)
def load_lstm_artifact(path=None):
    if torch is None:
        return None
    artifact_path = path or default_model_path()
    if not os.path.exists(artifact_path):
        return None
    checkpoint = torch.load(artifact_path, map_location="cpu")
    model = CartLSTMRecommender(
        product_count=len(checkpoint["product_to_index"]),
        event_count=len(checkpoint["event_to_index"]),
        embedding_dim=checkpoint["metadata"]["embedding_dim"],
        hidden_dim=checkpoint["metadata"]["hidden_dim"],
    )
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return {"model": model, **checkpoint}


def predict_lstm_product_ids(user_id, limit=8, exclude_product_id=None, model_path=None):
    artifact = load_lstm_artifact(model_path)
    if not artifact or not user_id:
        return []

    sequence_length = artifact["metadata"]["sequence_length"]
    product_to_index = artifact["product_to_index"]
    event_to_index = artifact["event_to_index"]
    index_to_product = {int(index): value for index, value in artifact["index_to_product"].items()}

    events = list(
        UserBehavior.objects.filter(user_id=user_id, event_type="ADDED_TO_CART").order_by("-created_at", "-id")[:sequence_length]
    )
    if not events:
        return []

    events = list(reversed(events))
    padded = [{"product_id": 0, "event_type": PAD_TOKEN}] * (sequence_length - len(events)) + [
        {"product_id": event.product_id, "event_type": event.event_type}
        for event in events
    ]
    product_sequence = [
        product_to_index.get(str(item["product_id"]), product_to_index.get("<UNK>", 1))
        for item in padded
    ]
    event_sequence = [
        event_to_index.get(item["event_type"], event_to_index[PAD_TOKEN])
        for item in padded
    ]

    with torch.no_grad():
        logits = artifact["model"](
            torch.tensor([product_sequence], dtype=torch.long),
            torch.tensor([event_sequence], dtype=torch.long),
        )
        probabilities = torch.softmax(logits, dim=-1)[0]
        top_indices = torch.topk(probabilities, k=min(limit + 5, probabilities.shape[0])).indices.tolist()

    history_product_ids = {event.product_id for event in events}
    if exclude_product_id:
        history_product_ids.add(int(exclude_product_id))

    product_ids = []
    available_ids = set(ProductDocument.objects.values_list("product_id", flat=True))
    for index in top_indices:
        product_id_token = index_to_product.get(int(index))
        if not product_id_token or product_id_token in {"<PAD>", "<UNK>"}:
            continue
        product_id = int(product_id_token)
        if product_id in history_product_ids or product_id not in available_ids:
            continue
        product_ids.append(product_id)
        if len(product_ids) >= limit:
            break
    return product_ids


def lstm_recommendation_products(user_id, limit=8, exclude_product_id=None):
    ids = predict_lstm_product_ids(user_id, limit=limit, exclude_product_id=exclude_product_id)
    if not ids:
        return []
    products = {product.product_id: product for product in ProductDocument.objects.filter(product_id__in=ids)}
    return [products[product_id] for product_id in ids if product_id in products]
