import os
from decimal import Decimal

import requests


class ProductServiceError(Exception):
    pass


def fetch_product(product_id):
    base_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003").rstrip("/")
    response = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)
    if response.status_code == 404:
        raise ProductServiceError("Product not found")
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise ProductServiceError(payload.get("error", {}).get("message", "Product lookup failed"))
    product = payload["data"]
    inventory = product.get("inventory") or {}
    if product.get("status") != "ACTIVE":
        raise ProductServiceError("Product is not active")
    return {
        "id": product["id"],
        "name": product["name"],
        "price": Decimal(str(product["price"])),
        "image_url": _primary_image(product),
        "available_quantity": int(inventory.get("available_quantity") or 0),
    }


def _primary_image(product):
    for image in product.get("images", []):
        if image.get("is_primary"):
            return image.get("image_url")
    images = product.get("images", [])
    return images[0].get("image_url") if images else None

