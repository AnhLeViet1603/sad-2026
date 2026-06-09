import os
import random

from django.core.management.base import BaseCommand, CommandError

from chatbot.ml.lstm_dataset import build_sequence_dataset, load_behavior_rows_from_csv, load_behavior_rows_from_db
from chatbot.ml.lstm_model import CartLSTMRecommender, torch


class Command(BaseCommand):
    help = "Train a PyTorch LSTM recommender for add-to-cart product prediction."

    def add_arguments(self, parser):
        parser.add_argument("--csv", dest="csv_path", default=None)
        parser.add_argument("--epochs", type=int, default=8)
        parser.add_argument("--batch-size", type=int, default=32)
        parser.add_argument("--sequence-length", type=int, default=5)
        parser.add_argument("--min-events-per-user", type=int, default=3)
        parser.add_argument("--embedding-dim", type=int, default=64)
        parser.add_argument("--hidden-dim", type=int, default=96)
        parser.add_argument("--output-dir", default=None)

    def handle(self, *args, **options):
        if torch is None:
            raise CommandError("PyTorch is not installed. Install torch before training the LSTM recommender.")

        rows = (
            load_behavior_rows_from_csv(options["csv_path"])
            if options["csv_path"]
            else load_behavior_rows_from_db(event_type="ADDED_TO_CART")
        )
        dataset = build_sequence_dataset(
            rows,
            sequence_length=options["sequence_length"],
            min_events_per_user=options["min_events_per_user"],
        )
        if not dataset.targets:
            raise CommandError("Not enough behavior sequences to train. Add more events or lower --min-events-per-user.")

        indices = list(range(len(dataset.targets)))
        random.Random(42).shuffle(indices)
        split_at = max(1, int(len(indices) * 0.8))
        train_indices = indices[:split_at]
        val_indices = indices[split_at:] or indices[:1]

        model = CartLSTMRecommender(
            product_count=len(dataset.product_to_index),
            event_count=len(dataset.event_to_index),
            embedding_dim=options["embedding_dim"],
            hidden_dim=options["hidden_dim"],
        )
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = torch.nn.CrossEntropyLoss(ignore_index=0)

        train_tensors = _tensors(dataset, train_indices)
        val_tensors = _tensors(dataset, val_indices)

        for epoch in range(1, options["epochs"] + 1):
            model.train()
            epoch_loss = 0.0
            for products, events, targets in _batches(train_tensors, options["batch_size"]):
                optimizer.zero_grad()
                logits = model(products, events)
                loss = criterion(logits, targets)
                loss.backward()
                optimizer.step()
                epoch_loss += float(loss.item())

            top1, top5 = _evaluate(model, val_tensors)
            self.stdout.write(
                f"epoch={epoch} loss={epoch_loss:.4f} val_top1={top1:.4f} val_top5={top5:.4f}"
            )

        output_dir = options["output_dir"] or os.getenv("AI_MODEL_DIR", os.path.join(os.getcwd(), "models"))
        os.makedirs(output_dir, exist_ok=True)
        artifact_path = os.path.join(output_dir, "cart_lstm_recommender.pt")
        torch.save(
            {
                "model_state": model.state_dict(),
                "product_to_index": dataset.product_to_index,
                "index_to_product": dataset.index_to_product,
                "event_to_index": dataset.event_to_index,
                "metadata": {
                    "sequence_length": dataset.sequence_length,
                    "embedding_dim": options["embedding_dim"],
                    "hidden_dim": options["hidden_dim"],
                    "train_samples": len(train_indices),
                    "validation_samples": len(val_indices),
                },
            },
            artifact_path,
        )
        self.stdout.write(self.style.SUCCESS(f"Saved LSTM recommender artifact to {artifact_path}"))


def _tensors(dataset, indices):
    return (
        torch.tensor([dataset.product_sequences[index] for index in indices], dtype=torch.long),
        torch.tensor([dataset.event_sequences[index] for index in indices], dtype=torch.long),
        torch.tensor([dataset.targets[index] for index in indices], dtype=torch.long),
    )


def _batches(tensors, batch_size):
    products, events, targets = tensors
    for start in range(0, len(targets), batch_size):
        end = start + batch_size
        yield products[start:end], events[start:end], targets[start:end]


def _evaluate(model, tensors):
    model.eval()
    products, events, targets = tensors
    with torch.no_grad():
        logits = model(products, events)
        top5 = torch.topk(logits, k=min(5, logits.shape[1]), dim=1).indices
        top1_hits = (top5[:, 0] == targets).float().mean().item()
        top5_hits = (top5 == targets.unsqueeze(1)).any(dim=1).float().mean().item()
    return top1_hits, top5_hits
