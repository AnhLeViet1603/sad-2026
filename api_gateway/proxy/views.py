import os

import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from common.views import health_response


ROUTES = {
    "users": "USER_SERVICE_URL",
    "staff": "STAFF_SERVICE_URL",
    "products": "PRODUCT_SERVICE_URL",
    "cart": "CART_SERVICE_URL",
    "orders": "ORDER_SERVICE_URL",
    "payments": "PAYMENT_SERVICE_URL",
    "shipping": "SHIPPING_SERVICE_URL",
    "comments": "COMMENT_SERVICE_URL",
    "ai": "AI_SERVICE_URL",
}


@api_view(["GET"])
def health(request):
    return health_response("api_gateway")


@csrf_exempt
def proxy(request, path):
    service_key = path.split("/", 1)[0]
    env_name = ROUTES.get(service_key)
    if not env_name:
        return _gateway_error("ROUTE_NOT_FOUND", f"No route configured for /api/{path}", status=404)

    base_url = os.getenv(env_name)
    if not base_url:
        return _gateway_error("SERVICE_NOT_CONFIGURED", f"{env_name} is not configured", status=500)

    target_url = f"{base_url.rstrip('/')}/api/{path}"
    headers = _forward_headers(request)
    try:
        response = requests.request(
            method=request.method,
            url=target_url,
            params=request.GET,
            data=request.body,
            headers=headers,
            timeout=15,
        )
    except requests.RequestException:
        return _gateway_error("SERVICE_UNAVAILABLE", f"{service_key} service is unavailable", status=503)

    content_type = response.headers.get("Content-Type", "application/json")
    return HttpResponse(response.content, status=response.status_code, content_type=content_type)


def _forward_headers(request):
    skipped = {"host", "content-length", "connection"}
    headers = {key: value for key, value in request.headers.items() if key.lower() not in skipped}
    if request.user_id:
        headers["X-User-Id"] = str(request.user_id)
    if request.user_role:
        headers["X-User-Role"] = str(request.user_role)
    return headers


def _gateway_error(code, message, status):
    return JsonResponse({"success": False, "error": {"code": code, "message": message}}, status=status)
