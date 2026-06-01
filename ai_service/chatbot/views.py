import requests
from django.db.models import Count
from rest_framework.decorators import api_view

from chatbot.models import ChatMessage, ChatSession, ProductDocument, RecommendationLog, UserBehavior
from chatbot.serializers import ChatSerializer, TrackSerializer
from chatbot.services import product_payload, search_products, sync_products_from_service
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
def track(request):
    if not request.user_id:
        return error("UNAUTHORIZED", "Authentication token is required", status=401)
    serializer = TrackSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    behavior = UserBehavior.objects.create(user_id=request.user_id, **serializer.validated_data)
    return ok({"id": behavior.id}, "Behavior tracked", status=201)


@api_view(["GET"])
def home_recommendations(request):
    user_id = request.query_params.get("user_id") or request.user_id
    products = []
    source = "popular"

    if user_id:
        categories = (
            UserBehavior.objects.filter(user_id=user_id)
            .values("product_id")
            .annotate(score=Count("id"))
            .order_by("-score")
            .values_list("product_id", flat=True)[:5]
        )
        seen_products = ProductDocument.objects.filter(product_id__in=list(categories))
        category_names = [product.category for product in seen_products if product.category]
        if category_names:
            products = list(ProductDocument.objects.filter(category__in=category_names).exclude(product_id__in=list(categories))[:8])
            source = "behavior"

    if not products:
        products = list(ProductDocument.objects.order_by("price")[:8])

    payload = [product_payload(product) for product in products]
    RecommendationLog.objects.create(user_id=user_id, product_ids=[item["id"] for item in payload], source=source)
    return ok({"source": source, "products": payload})


@api_view(["POST"])
def chat(request):
    serializer = ChatSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    session_id = serializer.validated_data.get("session_id")
    if session_id:
        session = ChatSession.objects.filter(id=session_id).first()
    else:
        session = None
    if session is None:
        session = ChatSession.objects.create(user_id=request.user_id)

    message = serializer.validated_data["message"]
    ChatMessage.objects.create(session=session, role="user", content=message)

    products = [product_payload(product) for product in search_products(message, limit=5)]
    if products:
        answer = "Mình gợi ý các sản phẩm phù hợp nhất với nhu cầu của bạn dựa trên tên, mô tả và nhóm sản phẩm demo."
    else:
        answer = "Mình chưa tìm thấy sản phẩm thật phù hợp. Bạn có thể hỏi theo chủ đề như lập trình, AI, kinh tế hoặc kỹ năng."

    ChatMessage.objects.create(session=session, role="assistant", content=answer, products=products)
    RecommendationLog.objects.create(
        user_id=request.user_id,
        query=message,
        product_ids=[product["id"] for product in products],
        source="mock_chat",
    )
    return ok({"session_id": session.id, "answer": answer, "products": products})

