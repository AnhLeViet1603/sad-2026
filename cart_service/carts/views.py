import requests
from django.db import transaction
from rest_framework.decorators import api_view

from carts.models import Cart, CartItem
from carts.serializers import AddItemSerializer, CartSerializer, UpdateItemSerializer
from carts.services import ProductServiceError, fetch_product
from common.responses import error, ok
from common.views import health_response


@api_view(["GET"])
def health(request):
    return health_response("cart_service")


def _require_user_id(request):
    if not request.user_id:
        return None, error("UNAUTHORIZED", "Authentication token is required", status=401)
    return int(request.user_id), None


def _active_cart(user_id):
    cart, _ = Cart.objects.get_or_create(user_id=user_id, status="ACTIVE")
    return cart


@api_view(["GET"])
def current_cart(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error
    return ok(CartSerializer(_active_cart(user_id)).data)


@api_view(["POST"])
def add_item(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    serializer = AddItemSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    try:
        product = fetch_product(serializer.validated_data["product_id"])
    except ProductServiceError as exc:
        return error("PRODUCT_UNAVAILABLE", str(exc), status=400)
    except requests.RequestException:
        return error("PRODUCT_SERVICE_ERROR", "Product Service is unavailable", status=503)

    quantity = serializer.validated_data["quantity"]
    if product["available_quantity"] < quantity:
        return error("OUT_OF_STOCK", "Product stock is not enough", status=400)

    with transaction.atomic():
        cart = _active_cart(user_id)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product["id"],
            defaults={
                "product_name": product["name"],
                "product_price": product["price"],
                "quantity": quantity,
                "image_url": product["image_url"],
            },
        )
        if not created:
            new_quantity = item.quantity + quantity
            if product["available_quantity"] < new_quantity:
                return error("OUT_OF_STOCK", "Product stock is not enough", status=400)
            item.quantity = new_quantity
            item.product_name = product["name"]
            item.product_price = product["price"]
            item.image_url = product["image_url"]
            item.save()

    return ok(CartSerializer(cart).data, "Item added")


@api_view(["PATCH", "DELETE"])
def item_detail(request, item_id):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error

    try:
        item = CartItem.objects.select_related("cart").get(id=item_id, cart__user_id=user_id, cart__status="ACTIVE")
    except CartItem.DoesNotExist:
        return error("CART_ITEM_NOT_FOUND", "Cart item not found", status=404)

    if request.method == "DELETE":
        cart = item.cart
        item.delete()
        return ok(CartSerializer(cart).data, "Item removed")

    serializer = UpdateItemSerializer(data=request.data)
    if not serializer.is_valid():
        return error("VALIDATION_ERROR", serializer.errors, status=400)

    try:
        product = fetch_product(item.product_id)
    except ProductServiceError as exc:
        return error("PRODUCT_UNAVAILABLE", str(exc), status=400)
    except requests.RequestException:
        return error("PRODUCT_SERVICE_ERROR", "Product Service is unavailable", status=503)

    quantity = serializer.validated_data["quantity"]
    if product["available_quantity"] < quantity:
        return error("OUT_OF_STOCK", "Product stock is not enough", status=400)

    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return ok(CartSerializer(item.cart).data, "Item updated")


@api_view(["DELETE"])
def clear_cart(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error
    cart = _active_cart(user_id)
    cart.items.all().delete()
    return ok(CartSerializer(cart).data, "Cart cleared")


@api_view(["GET"])
def checkout_data(request):
    user_id, auth_error = _require_user_id(request)
    if auth_error:
        return auth_error
    cart = _active_cart(user_id)
    if not cart.items.exists():
        return error("EMPTY_CART", "Cart is empty", status=400)
    return ok(CartSerializer(cart).data)

