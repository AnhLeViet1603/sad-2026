import requests
from django.db.models import Count
from rest_framework.decorators import api_view

from chatbot.models import ChatMessage, ChatSession, ProductDocument, RecommendationLog, UserBehavior
from chatbot.serializers import ChatSerializer, TrackSerializer
from chatbot.services import (
    generate_answer,
    graph_recommendation_products,
    hybrid_search,
    product_payload,
    rebuild_embeddings,
    sync_products_from_service,
    track_behavior_graph,
)
from common.responses import error, ok
from common.views import health_response


@api_view(["GET"])
def health(request):
    return health_response("ai_service")


@api_view(["POST"])
def sync_products(request):
    try:
        count = sync_products_from_service()
    except requests.RequestException:
        return error("PRODUCT_SERVICE_ERROR", "Product Service is unavailable", status=503)
    except RuntimeError as exc:
        return error("SYNC_FAILED", str(exc), status=400)
    return ok({"synced": count}, "Products synced")


@api_view(["POST"])
def rebuild_product_embeddings(request):
    count = rebuild_embeddings()
    return ok({"embedded": count}, "Embeddings rebuilt")


@api_view(["POST"])
def track(request):
    if not request.user_id:
        return error("UNAUTHORIZED", "Authentication token is required", status=401)
    serializer = TrackSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    behavior = UserBehavior.objects.create(user_id=request.user_id, **serializer.validated_data)
    track_behavior_graph(request.user_id, serializer.validated_data["product_id"], serializer.validated_data["event_type"])
    return ok({"id": behavior.id}, "Behavior tracked", status=201)


@api_view(["GET"])
def home_recommendations(request):
    user_id = request.query_params.get("user_id") or request.user_id
    products = []
    source = "popular"

    graph_products = graph_recommendation_products(user_id, limit=8)
    if graph_products:
        products = graph_products
        source = "neo4j_graph"

    if not products and user_id:
        top_product_ids = (
            UserBehavior.objects.filter(user_id=user_id)
            .values("product_id")
            .annotate(score=Count("id"))
            .order_by("-score")
            .values_list("product_id", flat=True)[:5]
        )
        seen_products = ProductDocument.objects.filter(product_id__in=list(top_product_ids))
        category_names = [product.category for product in seen_products if product.category]
        if category_names:
            products = list(ProductDocument.objects.filter(category__in=category_names).exclude(product_id__in=list(top_product_ids))[:8])
            source = "behavior"

    if not products:
        products = list(ProductDocument.objects.order_by("price")[:8])

    payload = [product_payload(product, sources=[source]) for product in products]
    RecommendationLog.objects.create(user_id=user_id, product_ids=[item["id"] for item in payload], source=source)
    return ok({"source": source, "products": payload})


@api_view(["GET"])
def search(request):
    query = request.query_params.get("q", "")
    results = hybrid_search(query, user_id=request.user_id, limit=8)
    payload = [product_payload(item["product"], item["sources"], item.get("score")) for item in results]
    RecommendationLog.objects.create(
        user_id=request.user_id,
        query=query,
        product_ids=[item["id"] for item in payload],
        source="hybrid",
    )
    return ok({"query": query, "products": payload})


@api_view(["POST"])
def chat(request):
    serializer = ChatSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    session_id = serializer.validated_data.get("session_id")
    session = ChatSession.objects.filter(id=session_id).first() if session_id else None
    if session is None:
        session = ChatSession.objects.create(user_id=request.user_id)

    message = serializer.validated_data["message"]
    ChatMessage.objects.create(session=session, role="user", content=message)

    results = hybrid_search(message, user_id=request.user_id, limit=5)
    products = [product_payload(item["product"], item["sources"], item.get("score")) for item in results]
    answer = generate_answer(message, products)

    ChatMessage.objects.create(session=session, role="assistant", content=answer, products=products)
    RecommendationLog.objects.create(
        user_id=request.user_id,
        query=message,
        product_ids=[product["id"] for product in products],
        source="rag_gemini",
    )
    return ok(
        {
            "session_id": session.id,
            "answer": answer,
            "products": products,
            "retrieval": [{"product_id": product["id"], "sources": product["sources"]} for product in products],
        }
    )
