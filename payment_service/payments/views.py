from rest_framework.decorators import api_view

from common.responses import error, ok
from common.views import health_response
from payments.models import Payment, PaymentTransaction
from payments.serializers import CreatePaymentSerializer, PaymentSerializer


@api_view(["GET"])
def health(request):
    return health_response("payment_service")


@api_view(["GET", "POST"])
def payment_collection(request):
    if request.method == "GET":
        order_id = request.query_params.get("order_id")
        queryset = Payment.objects.prefetch_related("transactions").order_by("-created_at")
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return ok(PaymentSerializer(queryset, many=True).data)

    serializer = CreatePaymentSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    payment = Payment.objects.create(**serializer.validated_data)
    PaymentTransaction.objects.create(payment=payment, status=payment.status, message="Payment created")
    return ok(PaymentSerializer(payment).data, "Payment created", status=201)


@api_view(["GET"])
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.prefetch_related("transactions").get(id=payment_id)
    except Payment.DoesNotExist:
        return error("PAYMENT_NOT_FOUND", "Payment not found", status=404)
    return ok(PaymentSerializer(payment).data)


def _simulate(payment_id, status, message):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return error("PAYMENT_NOT_FOUND", "Payment not found", status=404)

    payment.status = status
    payment.provider_reference = f"DEMO-{payment.id:08d}"
    payment.save(update_fields=["status", "provider_reference", "updated_at"])
    PaymentTransaction.objects.create(payment=payment, status=status, message=message)
    return ok(PaymentSerializer(payment).data, message)


@api_view(["POST"])
def simulate_success(request, payment_id):
    return _simulate(payment_id, "SUCCESS", "Payment simulated as successful")


@api_view(["POST"])
def simulate_failed(request, payment_id):
    return _simulate(payment_id, "FAILED", "Payment simulated as failed")


@api_view(["POST"])
def callback(request):
    payment_id = request.data.get("payment_id")
    status = request.data.get("status")
    if status not in {"SUCCESS", "FAILED", "CANCELLED"}:
        return error("VALIDATION_ERROR", "`status` must be SUCCESS, FAILED, or CANCELLED", status=400)
    return _simulate(payment_id, status, f"Payment callback received: {status}")

