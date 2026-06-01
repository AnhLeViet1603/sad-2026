import os
from decimal import Decimal

import requests

from chatbot.models import ProductDocument


def sync_products_from_service():
    base_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003").rstrip("/")
    response = requests.get(f"{base_url}/api/products/ai/export", timeout=10)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError("Product export failed")

    count = 0
    for item in payload["data"]:
        ProductDocument.objects.update_or_create(
            product_id=item["id"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "category": item.get("category"),
                "brand": item.get("brand"),
                "price": Decimal(str(item["price"])),
                "stock": int(item.get("stock") or 0),
            },
        )
        count += 1
    return count


def search_products(query, limit=5):
    queryset = ProductDocument.objects.all()
    if query:
        words = [word.lower() for word in query.split() if len(word) > 1]
        for word in words[:5]:
            queryset = queryset.filter(description__icontains=word) | ProductDocument.objects.filter(name__icontains=word)
    return list(queryset.order_by("price")[:limit])


def product_payload(product):
    return {
        "id": product.product_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "brand": product.brand,
        "price": str(product.price),
        "stock": product.stock,
    }

