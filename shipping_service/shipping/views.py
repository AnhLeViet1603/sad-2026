from rest_framework.decorators import api_view

from common.permissions import STAFF_ROLES, require_staff, require_user, role_name
from common.responses import error, ok
from common.views import health_response
from shipping.models import Shipment, ShippingStatusHistory
from shipping.serializers import CreateShipmentSerializer, ShipmentSerializer, ShippingFeeSerializer, UpdateShipmentStatusSerializer


@api_view(["GET"])
def health(request):
    return health_response("shipping_service")


def _tracking_code(order_id):
    return f"SHIP-{int(order_id):08d}"


@api_view(["POST"])
def shipping_fee(request):
    serializer = ShippingFeeSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    province = (serializer.validated_data.get("province") or "").lower()
    fee = 25000 if "hồ chí minh" in province or "ho chi minh" in province else 30000
    return ok({"shipping_fee": fee})


@api_view(["GET", "POST"])
def shipment_collection(request):
    user_id, auth_error = require_user(request)
    if auth_error:
        return auth_error

    if request.method == "GET":
        order_id = request.query_params.get("order_id")
        queryset = Shipment.objects.prefetch_related("history").order_by("-created_at")
        if role_name(request) not in STAFF_ROLES:
            queryset = queryset.filter(user_id=user_id)
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return ok(ShipmentSerializer(queryset, many=True).data)

    serializer = CreateShipmentSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)
    if role_name(request) not in STAFF_ROLES and serializer.validated_data["user_id"] != user_id:
        return error("FORBIDDEN", "You cannot create a shipment for another user", status=403)

    shipment = Shipment.objects.create(
        **serializer.validated_data,
        tracking_code=_tracking_code(serializer.validated_data["order_id"]),
    )
    ShippingStatusHistory.objects.create(shipment=shipment, status=shipment.status, note="Shipment created")
    return ok(ShipmentSerializer(shipment).data, "Shipment created", status=201)


@api_view(["GET"])
def shipment_detail(request, shipment_id):
    user_id, auth_error = require_user(request)
    if auth_error:
        return auth_error

    try:
        shipment = Shipment.objects.prefetch_related("history").get(id=shipment_id)
    except Shipment.DoesNotExist:
        return error("SHIPMENT_NOT_FOUND", "Shipment not found", status=404)
    if role_name(request) not in STAFF_ROLES and shipment.user_id != user_id:
        return error("FORBIDDEN", "You cannot access this shipment", status=403)
    return ok(ShipmentSerializer(shipment).data)


@api_view(["GET"])
def tracking(request, tracking_code):
    try:
        shipment = Shipment.objects.prefetch_related("history").get(tracking_code=tracking_code)
    except Shipment.DoesNotExist:
        return error("SHIPMENT_NOT_FOUND", "Shipment not found", status=404)
    return ok(ShipmentSerializer(shipment).data)


@api_view(["PATCH"])
def update_status(request, shipment_id):
    auth_error = require_staff(request)
    if auth_error:
        return auth_error

    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        return error("SHIPMENT_NOT_FOUND", "Shipment not found", status=404)

    serializer = UpdateShipmentStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    shipment.status = serializer.validated_data["status"]
    shipment.save(update_fields=["status", "updated_at"])
    ShippingStatusHistory.objects.create(
        shipment=shipment,
        status=shipment.status,
        note=serializer.validated_data.get("note"),
    )
    return ok(ShipmentSerializer(shipment).data, "Shipment status updated")
