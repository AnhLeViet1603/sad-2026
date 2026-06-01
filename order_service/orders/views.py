from decimal import Decimal

import requests
from django.db import transaction
from rest_framework.decorators import api_view

from common.responses import error, ok
from common.views import health_response
from orders.models import Order, OrderItem, OrderStatusHistory
from orders.serializers import CheckoutSerializer, OrderSerializer, UpdateOrderStatusSerializer
from orders.services import DownstreamServiceError, clear_cart, create_payment, create_shipment, get_checkout_cart


@api_view(["GET"])
def health(request):
    return health_response("order_service")


def _require_user_id(request):
    if not request.user_id:
        return None, error("UNAUTHORIZED", "Authentication token is required", status=401)
    return int(request.user_id), None


@api_view(["GET"])
def order_collection(request):
    queryset = Order.objects.prefetch_related("items", "history").order_by("-created_at")
    if request.user_id:
        queryset = queryset.filter(user_id=request.user_id)
    return ok(OrderSerializer(queryset, many=True).data)


@api_view(["POST"])
def checkout(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    serializer = CheckoutSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    try:
        cart = get_checkout_cart(request)
    except DownstreamServiceError as exc:
        return error("CHECKOUT_FAILED", str(exc), status=400)
    except requests.RequestException:
        return error("CART_SERVICE_ERROR", "Cart Service is unavailable", status=503)

    items = cart.get("items", [])
    if not items:
        return error("EMPTY_CART", "Cart is empty", status=400)

    shipping_address = serializer.validated_data["shipping_address"]
    shipping_fee = Decimal("30000.00")
    item_total = Decimal(str(cart["total_amount"]))

    with transaction.atomic():
        order = Order.objects.create(
            user_id=user_id,
            total_amount=item_total + shipping_fee,
            shipping_fee=shipping_fee,
            receiver_name=shipping_address["receiver_name"],
            phone=shipping_address["phone"],
            province=shipping_address["province"],
            district=shipping_address["district"],
            ward=shipping_address["ward"],
            detail=shipping_address["detail"],
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                product_name=item["product_name"],
                product_price=item["product_price"],
                quantity=item["quantity"],
                line_total=item["line_total"],
                image_url=item.get("image_url"),
            )
        OrderStatusHistory.objects.create(order=order, status=order.status, note="Order created from cart")

    try:
        payment = create_payment(order, serializer.validated_data["payment_method"])
        shipment = create_shipment(order)
        clear_cart(request)
    except DownstreamServiceError as exc:
        return error("CHECKOUT_PARTIAL_FAILURE", str(exc), status=502)
    except requests.RequestException:
        return error("CHECKOUT_PARTIAL_FAILURE", "A downstream service is unavailable", status=503)

    order.payment_id = payment["id"]
    order.payment_status = payment["status"]
    order.shipment_id = shipment["id"]
    order.shipping_status = shipment["status"]
    order.tracking_code = shipment["tracking_code"]
    order.save(
        update_fields=[
            "payment_id",
            "payment_status",
            "shipment_id",
            "shipping_status",
            "tracking_code",
            "updated_at",
        ]
    )
    return ok(OrderSerializer(order).data, "Checkout completed", status=201)


@api_view(["GET"])
def order_detail(request, order_id):
    try:
        order = Order.objects.prefetch_related("items", "history").get(id=order_id)
    except Order.DoesNotExist:
        return error("ORDER_NOT_FOUND", "Order not found", status=404)

    if request.user_id and order.user_id != int(request.user_id):
        return error("FORBIDDEN", "You cannot access this order", status=403)
    return ok(OrderSerializer(order).data)


@api_view(["PATCH"])
def update_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return error("ORDER_NOT_FOUND", "Order not found", status=404)

    serializer = UpdateOrderStatusSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    order.status = serializer.validated_data["status"]
    order.save(update_fields=["status", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        status=order.status,
        note=serializer.validated_data.get("note"),
    )
    return ok(OrderSerializer(order).data, "Order status updated")

