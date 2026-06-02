import hashlib
import math
import os
from decimal import Decimal

import requests
from django.db.models import Q
from neo4j import GraphDatabase
from pgvector.django import CosineDistance

from chatbot.models import ProductDocument


VECTOR_DIMENSIONS = 3072


class GeminiError(Exception):
    pass


def build_document(item):
    parts = [
        item.get("name") or "",
        item.get("description") or "",
        item.get("category") or "",
        item.get("brand") or "",
        f"price {item.get('price')}",
        f"stock {item.get('stock')}",
    ]
    return "\n".join(part for part in parts if part)


def sync_products_from_service():
    base_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8003").rstrip("/")
    response = requests.get(f"{base_url}/api/products/ai/export", timeout=10)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError("Product export failed")

    count = 0
    for item in payload["data"]:
        document = build_document(item)
        product, _ = ProductDocument.objects.update_or_create(
            product_id=item["id"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "category": item.get("category"),
                "brand": item.get("brand"),
                "price": Decimal(str(item["price"])),
                "stock": int(item.get("stock") or 0),
                "document": document,
            },
        )
        upsert_product_node(product)
        count += 1
    return count


def rebuild_embeddings():
    count = 0
    for product in ProductDocument.objects.all():
        product.embedding = embed_text(product.document)
        product.save(update_fields=["embedding", "updated_at"])
        count += 1
    return count


def embed_text(text):
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_embedding(text)
        except (GeminiError, requests.RequestException):
            pass
    return deterministic_embedding(text)


def gemini_embedding(text):
    model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent"
    response = requests.post(
        url,
        headers={"x-goog-api-key": api_key},
        json={"content": {"parts": [{"text": text[:12000]}]}},
        timeout=20,
    )
    response.raise_for_status()
    values = response.json().get("embedding", {}).get("values")
    if not values:
        raise GeminiError("Gemini embedding response did not include values")
    return normalize_dimensions(values)


def deterministic_embedding(text):
    vector = [0.0] * VECTOR_DIMENSIONS
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % VECTOR_DIMENSIONS
        sign = 1 if digest[4] % 2 == 0 else -1
        vector[index] += sign
    return normalize_dimensions(vector)


def normalize_dimensions(values):
    vector = [float(value) for value in values[:VECTOR_DIMENSIONS]]
    if len(vector) < VECTOR_DIMENSIONS:
        vector.extend([0.0] * (VECTOR_DIMENSIONS - len(vector)))
    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def keyword_search(query, limit=8):
    queryset = ProductDocument.objects.all()
    words = [word for word in query.split() if len(word) > 1]
    if words:
        condition = Q()
        for word in words[:8]:
            condition |= Q(name__icontains=word) | Q(description__icontains=word) | Q(category__icontains=word)
        queryset = queryset.filter(condition)
    return list(queryset.order_by("price")[:limit])


def vector_search(query, limit=8):
    query_vector = embed_text(query)
    return list(
        ProductDocument.objects.filter(embedding__isnull=False)
        .annotate(distance=CosineDistance("embedding", query_vector))
        .order_by("distance")[:limit]
    )


def hybrid_search(query, user_id=None, limit=8):
    scored = {}

    for rank, product in enumerate(keyword_search(query, limit=limit), start=1):
        scored.setdefault(product.product_id, {"product": product, "score": 0, "sources": set()})
        scored[product.product_id]["score"] += 1 / rank
        scored[product.product_id]["sources"].add("keyword")

    for rank, product in enumerate(vector_search(query, limit=limit), start=1):
        scored.setdefault(product.product_id, {"product": product, "score": 0, "sources": set()})
        scored[product.product_id]["score"] += 1.5 / rank
        scored[product.product_id]["sources"].add("vector")

    for rank, product in enumerate(graph_recommendation_products(user_id, limit=limit), start=1):
        scored.setdefault(product.product_id, {"product": product, "score": 0, "sources": set()})
        scored[product.product_id]["score"] += 1 / rank
        scored[product.product_id]["sources"].add("graph")

    ranked = sorted(scored.values(), key=lambda item: item["score"], reverse=True)[:limit]
    return [{"product": item["product"], "sources": sorted(item["sources"])} for item in ranked]


def generate_answer(message, products):
    context = "\n".join(
        f"- {product['name']} | {product['category']} | {product['price']} VND | {product['description']}"
        for product in products
    )
    prompt = (
        "Bạn là chatbot tư vấn sản phẩm cho demo e-commerce sách. "
        "Chỉ tư vấn dựa trên context sản phẩm bên dưới, trả lời ngắn gọn bằng tiếng Việt.\n\n"
        f"Câu hỏi: {message}\n\nContext:\n{context}"
    )
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_generate(prompt)
        except (GeminiError, requests.RequestException):
            pass
    if products:
        names = ", ".join(product["name"] for product in products[:3])
        return f"Mình gợi ý {names}. Các sản phẩm này phù hợp nhất với nội dung bạn hỏi trong dữ liệu demo."
    return "Mình chưa tìm thấy sản phẩm phù hợp trong dữ liệu demo."


def gemini_generate(prompt):
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    api_key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    response = requests.post(
        url,
        headers={"x-goog-api-key": api_key},
        json={"contents": [{"role": "user", "parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    candidates = response.json().get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    text = "".join(part.get("text", "") for part in parts).strip()
    if not text:
        raise GeminiError("Gemini response did not include text")
    return text


def product_payload(product, sources=None):
    return {
        "id": product.product_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "brand": product.brand,
        "price": str(product.price),
        "stock": product.stock,
        "sources": sources or [],
    }


def neo4j_driver():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not uri or not user or not password:
        return None
    return GraphDatabase.driver(uri, auth=(user, password))


def upsert_product_node(product):
    driver = neo4j_driver()
    if not driver:
        return
    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (p:Product {id: $product_id})
                SET p.name = $name, p.category = $category, p.brand = $brand, p.price = $price
                WITH p
                MERGE (c:Category {name: coalesce($category, 'Uncategorized')})
                MERGE (p)-[:IN_CATEGORY]->(c)
                """,
                product_id=product.product_id,
                name=product.name,
                category=product.category,
                brand=product.brand,
                price=float(product.price),
            )
    finally:
        driver.close()


def track_behavior_graph(user_id, product_id, event_type):
    driver = neo4j_driver()
    if not driver:
        return
    relation = event_type if event_type in {"VIEWED", "ADDED_TO_CART", "PURCHASED", "RATED"} else "VIEWED"
    try:
        with driver.session() as session:
            session.run(
                f"""
                MERGE (u:User {{id: $user_id}})
                MERGE (p:Product {{id: $product_id}})
                MERGE (u)-[r:{relation}]->(p)
                SET r.count = coalesce(r.count, 0) + 1,
                    r.updated_at = datetime()
                """,
                user_id=int(user_id),
                product_id=int(product_id),
            )
    finally:
        driver.close()


def graph_recommendation_ids(user_id, limit=8):
    if not user_id:
        return []
    driver = neo4j_driver()
    if not driver:
        return []
    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {id: $user_id})-[r:VIEWED|ADDED_TO_CART|PURCHASED|RATED]->(:Product)-[:IN_CATEGORY]->(c:Category)<-[:IN_CATEGORY]-(rec:Product)
                WHERE NOT (u)-[:VIEWED|ADDED_TO_CART|PURCHASED|RATED]->(rec)
                WITH rec, sum(
                    CASE type(r)
                        WHEN 'PURCHASED' THEN 5
                        WHEN 'ADDED_TO_CART' THEN 3
                        WHEN 'RATED' THEN 2
                        ELSE 1
                    END * coalesce(r.count, 1)
                ) AS score
                RETURN rec.id AS product_id, score
                ORDER BY score DESC
                LIMIT $limit
                """,
                user_id=int(user_id),
                limit=limit,
            )
            return [record["product_id"] for record in result]
    finally:
        driver.close()


def graph_recommendation_products(user_id, limit=8):
    ids = graph_recommendation_ids(user_id, limit)
    if not ids:
        return []
    products = {product.product_id: product for product in ProductDocument.objects.filter(product_id__in=ids)}
    return [products[product_id] for product_id in ids if product_id in products]
