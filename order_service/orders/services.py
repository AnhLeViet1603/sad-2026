import os

import requests


class DownstreamServiceError(Exception):
    pass


def _headers(request):
    authorization = request.headers.get("Authorization")
    return {"Authorization": authorization} if authorization else {}


def _extract(response, service_name):
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        message = payload.get("error", {}).get("message", f"{service_name} request failed")
        raise DownstreamServiceError(message)
    return payload["data"]


def get_checkout_cart(request):
    base_url = os.getenv("CART_SERVICE_URL", "http://localhost:8004").rstrip("/")
    response = requests.get(f"{base_url}/api/cart/checkout-data", headers=_headers(request), timeout=5)
    return _extract(response, "Cart Service")


def clear_cart(request):
    base_url = os.getenv("CART_SERVICE_URL", "http://localhost:8004").rstrip("/")
    response = requests.delete(f"{base_url}/api/cart/clear", headers=_headers(request), timeout=5)
    return _extract(response, "Cart Service")


def create_payment(order, method, request=None):
    base_url = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8006").rstrip("/")
    response = requests.post(
        f"{base_url}/api/payments",
        json={"order_id": order.id, "user_id": order.user_id, "amount": str(order.total_amount), "method": method},
        headers=_headers(request) if request else {},
        timeout=5,
    )
    return _extract(response, "Payment Service")


def create_shipment(order, request=None):
    base_url = os.getenv("SHIPPING_SERVICE_URL", "http://localhost:8007").rstrip("/")
    response = requests.post(
        f"{base_url}/api/shipping/shipments",
        json={
            "order_id": order.id,
            "user_id": order.user_id,
            "receiver_name": order.receiver_name,
            "phone": order.phone,
            "province": order.province,
            "district": order.district,
            "ward": order.ward,
            "detail": order.detail,
            "shipping_fee": str(order.shipping_fee),
        },
        headers=_headers(request) if request else {},
        timeout=5,
    )
    return _extract(response, "Shipping Service")
