from django.db.models import Avg, Count
from rest_framework.decorators import api_view

from comments.models import CommentReply, Review
from comments.serializers import ReplySerializer, ReviewSerializer
from common.responses import error, ok
from common.views import health_response


@api_view(["GET"])
def health(request):
    return health_response("comment_service")


def _require_user_id(request):
    if not request.user_id:
        return None, error("UNAUTHORIZED", "Authentication token is required", status=401)
    return int(request.user_id), None


@api_view(["GET", "POST"])
def review_collection(request):
    if request.method == "GET":
        product_id = request.query_params.get("product_id")
        queryset = Review.objects.prefetch_related("replies").order_by("-created_at")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return ok(ReviewSerializer(queryset, many=True).data)

    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    serializer = ReviewSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    review = serializer.save(user_id=user_id)
    return ok(ReviewSerializer(review).data, "Review created", status=201)


@api_view(["GET"])
def product_reviews(request, product_id):
    queryset = Review.objects.prefetch_related("replies").filter(product_id=product_id).order_by("-created_at")
    return ok(ReviewSerializer(queryset, many=True).data)


@api_view(["GET"])
def rating_summary(request, product_id):
    summary = Review.objects.filter(product_id=product_id).aggregate(avg_rating=Avg("rating"), review_count=Count("id"))
    return ok(
        {
            "product_id": product_id,
            "avg_rating": round(summary["avg_rating"] or 0, 2),
            "review_count": summary["review_count"],
        }
    )


@api_view(["POST"])
def reply_review(request, review_id):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return error("REVIEW_NOT_FOUND", "Review not found", status=404)

    serializer = ReplySerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    reply = CommentReply.objects.create(review=review, user_id=user_id, content=serializer.validated_data["content"])
    return ok({"id": reply.id, "content": reply.content, "created_at": reply.created_at}, "Reply created", status=201)

