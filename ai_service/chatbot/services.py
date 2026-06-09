import hashlib
import math
import os
from decimal import Decimal

import requests
from neo4j import GraphDatabase
from pgvector.django import CosineDistance

from chatbot.models import ProductDocument


VECTOR_DIMENSIONS = 3072
SOURCE_LABELS = {
    "keyword": "matched your keywords",
    "vector": "semantically close to your question",
    "personalized": "related to your previous activity",
    "lstm": "often added to cart after products like the one you selected",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "i",
    "me",
    "my",
    "need",
    "product",
    "products",
    "the",
    "to",
    "want",
}
QUERY_EXPANSIONS = {
    "clean": ["cleaning", "vacuum", "cleaner"],
    "cleaning": ["clean", "vacuum", "cleaner"],
    "workout": ["fitness", "training", "dumbbell", "yoga", "sports"],
    "exercise": ["fitness", "training", "dumbbell", "yoga", "sports"],
    "sport": ["sports", "fitness", "training"],
    "sports": ["sport", "fitness", "training"],
    "kitchen": ["cookware", "fryer", "cooking"],
}


class GeminiError(Exception):
    pass


def build_document(item):
    type_details = item.get("type_details") or {}
    detail_text = " ".join(f"{key} {value}" for key, value in type_details.items() if value not in (None, ""))
    parts = [
        item.get("name") or "",
        item.get("description") or "",
        item.get("category") or "",
        item.get("brand") or "",
        item.get("product_type") or "",
        detail_text,
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
    synced_ids = []
    for item in payload["data"]:
        document = build_document(item)
        product, _ = ProductDocument.objects.update_or_create(
            product_id=item["id"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "category": item.get("category"),
                "brand": item.get("brand"),
                "product_type": item.get("product_type"),
                "type_details": item.get("type_details") or {},
                "price": Decimal(str(item["price"])),
                "stock": int(item.get("stock") or 0),
                "document": document,
            },
        )
        upsert_product_node(product)
        synced_ids.append(product.product_id)
        count += 1
    if synced_ids:
        ProductDocument.objects.exclude(product_id__in=synced_ids).delete()
        delete_stale_product_nodes(synced_ids)
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
    terms = query_terms(query)
    if not terms:
        return list(ProductDocument.objects.order_by("price")[:limit])

    scored = []
    for product in ProductDocument.objects.all():
        haystack = " ".join(
            [
                product.name or "",
                product.description or "",
                product.category or "",
                product.brand or "",
            ]
        ).lower()
        score = 0
        for term in terms:
            if term in haystack:
                score += 2 if term in (product.name or "").lower() else 1
        if score:
            scored.append((score, product))
    scored.sort(key=lambda item: (-item[0], item[1].price))
    return [product for _, product in scored[:limit]]


def query_terms(query):
    terms = []
    for raw in query.lower().replace(",", " ").replace(".", " ").split():
        term = "".join(character for character in raw if character.isalnum())
        if len(term) <= 1 or term in STOPWORDS:
            continue
        terms.append(term)
        terms.extend(QUERY_EXPANSIONS.get(term, []))
    return list(dict.fromkeys(terms))[:12]


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
        scored[product.product_id]["score"] += 3 / rank
        scored[product.product_id]["sources"].add("keyword")

    for rank, product in enumerate(vector_search(query, limit=limit), start=1):
        scored.setdefault(product.product_id, {"product": product, "score": 0, "sources": set()})
        scored[product.product_id]["score"] += 2 / rank
        scored[product.product_id]["sources"].add("vector")

    for rank, product in enumerate(graph_recommendation_products(user_id, limit=limit), start=1):
        scored.setdefault(product.product_id, {"product": product, "score": 0, "sources": set()})
        scored[product.product_id]["score"] += 0.35 / rank
        scored[product.product_id]["sources"].add("personalized")

    ranked = sorted(scored.values(), key=lambda item: item["score"], reverse=True)[:limit]
    return [
        {
            "product": item["product"],
            "sources": sorted(item["sources"]),
            "score": round(item["score"], 4),
        }
        for item in ranked
    ]


def generate_answer(message, products):
    context = "\n".join(
        (
            f"- {product['name']} | category: {product['category']} | brand: {product.get('brand') or 'N/A'} "
            f"| price: {product['price']} VND | why retrieved: {', '.join(product.get('reasons') or [])} "
            f"| description: {product['description']}"
        )
        for product in products
    )
    prompt = (
        "You are a shopping assistant for a general ecommerce store, not a bookstore. "
        "Answer in Vietnamese. Use only the product context below. "
        "First address the shopper's question directly, then recommend at most 3 products. "
        "For each recommendation, explain the concrete reason using product category, brand, description, or retrieval reason. "
        "If the context does not match the question, say that clearly and suggest the closest available alternatives.\n\n"
        f"Shopper question: {message}\n\nProduct context:\n{context}"
    )
    if os.getenv("GEMINI_API_KEY"):
        try:
            return gemini_generate(prompt)
        except (GeminiError, requests.RequestException):
            pass
    if products:
        return fallback_answer(message, products)
    return "Mình chưa tìm thấy sản phẩm phù hợp trong dữ liệu demo. Bạn có thể mô tả nhu cầu cụ thể hơn, ví dụ danh mục, ngân sách hoặc mục đích sử dụng."


def fallback_answer(message, products):
    lines = [f"Mình tìm trong catalog theo câu hỏi: \"{message}\"."]
    lines.append("Các lựa chọn gần nhất là:")
    for product in products[:3]:
        reasons = product.get("reasons") or ["phù hợp nhất trong dữ liệu hiện có"]
        lines.append(
            f"- {product['name']}: {product['category']}, giá {product['price']} VND. Lý do: {', '.join(reasons)}."
        )
    if any("personalized" in product.get("sources", []) for product in products[:3]):
        lines.append("Một vài gợi ý có dùng lịch sử xem/thêm giỏ/mua hàng của bạn để cá nhân hóa.")
    return "\n".join(lines)


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


def product_payload(product, sources=None, score=None):
    source_list = sources or []
    return {
        "id": product.product_id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "brand": product.brand,
        "product_type": product.product_type,
        "type_details": product.type_details,
        "price": str(product.price),
        "stock": product.stock,
        "sources": source_list,
        "reasons": [SOURCE_LABELS.get(source, source) for source in source_list],
        "score": score,
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


def delete_stale_product_nodes(active_product_ids):
    driver = neo4j_driver()
    if not driver:
        return
    try:
        with driver.session() as session:
            session.run(
                """
                MATCH (p:Product)
                WHERE NOT p.id IN $active_product_ids
                DETACH DELETE p
                """,
                active_product_ids=[int(product_id) for product_id in active_product_ids],
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
