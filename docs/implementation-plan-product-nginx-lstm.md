# Implementation Plan: Product Inheritance, Nginx Gateway, LSTM Recommendation

## Goal

Plan future implementation for three requested changes:

- Product Service: make `Product` the base model. Each product type must inherit from it, for example `Book`, `Laptop`, `Phone`, `Toy`, and so on. `Category` remains separate from product type, so a category like `Technology` can contain multiple product types such as `Toy`, `Phone`, and `Book`.
- API Gateway: replace the current Django API gateway with nginx-based routing.
- AI Service: add an LSTM model, including a training script, to predict/recommend products from user behavior.

## Confirmed Decisions

- Product inheritance strategy: Django multi-table inheritance.
- Existing product demo data: wipe and reseed cleanly.
- Product API: one shared `/api/products` collection/detail API using `product_type`.
- API Gateway: replace old Django gateway content; keep the `api_gateway/` folder only for nginx configuration.
- LSTM framework: PyTorch.
- LSTM objective: when a user adds one product to cart, recommend different products they may also add.
- Demo training data: generate a CSV with at least 500 behavior rows.
- Existing AI chat must keep working, including product sync and embedding rebuild.
- Commit after each major change.

## Current State

- Product Service currently has one concrete `Product` model with shared fields plus generic `ProductAttribute` and `ProductAttributeValue`.
- Product seed data currently creates generic ecommerce products grouped by category only.
- API Gateway currently runs as a Django service in `api_gateway/` and proxies `/api/<service>/...` using `requests`.
- There is already a simple `docker/nginx.conf`, but it only serves frontend static files and does not proxy backend services.
- AI Service already tracks `UserBehavior` with event types `VIEWED`, `ADDED_TO_CART`, `PURCHASED`, `RATED`.
- AI Service already supports product sync, embeddings, hybrid search, Neo4j graph recommendations, and chatbot endpoints.

## Phase 1: Product Domain Redesign

### Decisions to Confirm

- Use Django multi-table inheritance for typed products:
  - `Product` stores shared fields.
  - `Book(Product)`, `Laptop(Product)`, `Phone(Product)`, etc. store type-specific fields in their own tables.
- Keep `Category` independent from product type.
- Add a normalized product type identifier in responses, likely `product_type`, so clients and AI export can distinguish `Book` vs `Phone` while still filtering by category.
- Keep existing generic `ProductAttribute` support only if it is still needed for flexible/unknown attributes.
- Implement the shared API with `product_type` in request/response payloads.

### Proposed Minimum Product Types

At least 10 concrete product types:

1. `Book`
2. `Laptop`
3. `Phone`
4. `Toy`
5. `Tablet`
6. `Headphones`
7. `Camera`
8. `SmartWatch`
9. `HomeAppliance`
10. `Clothing`

Optional later types: `Furniture`, `BeautyProduct`, `SportsEquipment`, `GameConsole`, `Kitchenware`.

### Product Model Tasks

- Update `product_service/products/models.py`.
- Keep shared fields on `Product`:
  - `name`
  - `slug`
  - `description`
  - `price`
  - `category`
  - `brand`
  - `status`
  - `created_at`
- Add `product_type` helper/property or field strategy.
- Add concrete child models with type-specific fields, for example:
  - `Book`: `author`, `publisher`, `isbn`, `language`, `page_count`
  - `Laptop`: `cpu`, `ram_gb`, `storage_gb`, `gpu`, `screen_size_inch`
  - `Phone`: `os`, `storage_gb`, `ram_gb`, `camera_mp`, `battery_mah`
  - `Toy`: `age_range`, `material`, `safety_standard`
  - `Tablet`: `os`, `screen_size_inch`, `storage_gb`, `supports_pen`
  - `Headphones`: `connection_type`, `noise_cancelling`, `battery_hours`
  - `Camera`: `sensor_type`, `megapixels`, `lens_mount`, `video_resolution`
  - `SmartWatch`: `os`, `battery_days`, `water_resistant`, `health_features`
  - `HomeAppliance`: `appliance_type`, `power_watts`, `capacity`, `energy_rating`
  - `Clothing`: `size`, `color`, `material`, `gender`
- Generate migrations for clean reseeding; demo product data can be wiped.
- Update admin registration if admin is used.

### Serializer/API Tasks

- Update serializers to expose base fields plus type-specific payload.
- Add one polymorphic serializer that selects child serializer by `product_type`.
- Keep existing URLs stable where possible:
  - `GET /api/products`
  - `GET /api/products/<id>`
  - `GET /api/products/search`
  - `GET /api/products/ai/export`
- Add support for filtering by `product_type`.
- Ensure category filtering remains category-based only.
- Update `related_products` logic so it can recommend by category, product type, or both depending on desired UX.

### Seed Data Tasks

- Rewrite `product_service/products/management/commands/seed_products.py`.
- Create categories that intentionally mix product types, for example:
  - `Technology`: `Phone`, `Laptop`, `Book`, `Toy`
  - `Education`: `Book`, `Tablet`, `Toy`
  - `Entertainment`: `Camera`, `Headphones`, `Toy`, `Game/Book`
  - `Home`: `HomeAppliance`, `Book`, `Toy`
  - `Fashion & Lifestyle`: `Clothing`, `SmartWatch`, `Headphones`
- Seed at least one product for each of the 10 product types.
- Prefer 20-30 products total so search, recommendations, and frontend browsing remain meaningful.
- Include realistic type-specific fields for each seeded item.
- Update product image seed URLs and inventory creation.

### Compatibility Tasks

- Check downstream services that store only `product_id`, especially cart, order, comment, and AI services.
- Keep product IDs stable enough for foreign-service references, or document that local demo data can be reseeded.
- Update frontend assumptions if it renders `attribute_values` or expects only the old flat product shape.
- Update AI export to include:
  - `product_type`
  - type-specific fields
  - category
  - brand
  - price
  - stock

## Phase 2: Nginx API Gateway

### Gateway Design

- Replace the Django `api_gateway` container with an nginx gateway container.
- Route `/api/users/` to `user_service:8001`.
- Route `/api/staff/` to `staff_service:8002`.
- Route `/api/products/` to `product_service:8003`.
- Route `/api/cart/` to `cart_service:8004`.
- Route `/api/orders/` to `order_service:8005`.
- Route `/api/payments/` to `payment_service:8006`.
- Route `/api/shipping/` to `shipping_service:8007`.
- Route `/api/comments/` to `comment_service:8008`.
- Route `/api/ai/` to `ai_service:8009`.
- Preserve request method, body, query string, authorization header, and client headers needed by the existing services.

### Nginx Tasks

- Create a dedicated nginx config, for example `docker/api-gateway.nginx.conf`.
- Add upstream blocks for each service.
- Add `proxy_set_header` directives:
  - `Host`
  - `X-Real-IP`
  - `X-Forwarded-For`
  - `X-Forwarded-Proto`
  - `Authorization`
- Add a gateway health endpoint, for example `/health`, returning a static nginx response.
- Configure timeouts suitable for AI/chat endpoints.
- Configure CORS only if frontend currently relies on gateway-level CORS.

### Docker Compose Tasks

- Replace the `api_gateway` service build target with `nginx:alpine`.
- Mount the nginx gateway config read-only.
- Keep host port `8000:80` so frontend `VITE_API_BASE_URL=http://localhost:8000` continues to work.
- Update `depends_on` to include all backend services routed by nginx.
- Delete old Django gateway content and keep only nginx configuration in the `api_gateway/` folder.

### Verification Tasks

- Verify:
  - `GET http://localhost:8000/health`
  - `GET http://localhost:8000/api/products`
  - authenticated routes still receive `Authorization`
  - POST/PATCH/DELETE bodies pass through unchanged
  - AI chat/recommendation endpoints do not timeout too aggressively

## Phase 3: LSTM Product Prediction in AI Service

### Recommendation Design

- Use existing `UserBehavior` as the source event stream.
- Train a sequence model that predicts the next product a user may interact with.
- Convert behavior into ordered sessions/sequences per user:
  - input: recent product IDs and event types
  - target: next product ID, or next purchased/added product depending on chosen objective
- Include event weights or event embeddings so `PURCHASED` can matter more than `VIEWED`.

### Data Requirements

- Minimum useful fields:
  - `user_id`
  - `product_id`
  - `event_type`
  - `created_at`
- Optional features:
  - `product_type`
  - `category`
  - price bucket
  - brand
  - recency/time gap
- Need enough behavior rows for training. For demo/local development, add a behavior seeding script or synthetic dataset generator.

### Model Tasks

- Add PyTorch dependencies to `ai_service/requirements.txt` and Docker AI requirements.
- Add module structure, for example:
  - `ai_service/chatbot/ml/lstm_dataset.py`
  - `ai_service/chatbot/ml/lstm_model.py`
  - `ai_service/chatbot/ml/lstm_inference.py`
  - `ai_service/chatbot/management/commands/train_lstm_recommender.py`
- Store model artifacts under a configurable path, for example `AI_MODEL_DIR=/app/models`.
- Save:
  - trained model file
  - product ID vocabulary
  - event type vocabulary
  - metadata such as sequence length and training timestamp

### Training Script Tasks

- Add Django management command:
  - `python manage.py train_lstm_recommender`
- Support options:
  - `--epochs`
  - `--batch-size`
  - `--sequence-length`
  - `--min-events-per-user`
  - `--output-dir`
  - `--synthetic-demo-data` if real data is insufficient
- Training flow:
  - query `UserBehavior` ordered by `user_id`, `created_at`
  - build fixed-length product/event sequences
  - split train/validation
  - train LSTM classifier over product vocabulary
  - persist artifacts
  - print metrics such as validation top-1/top-5 accuracy

### Inference/API Tasks

- Add service function to load model lazily and predict product IDs for a user.
- Add endpoint, for example:
  - `GET /api/ai/recommendations/lstm`
- Integrate with `home_recommendations` as an optional source:
  - prefer LSTM when model artifact exists and user has enough history
  - fallback to graph recommendation
  - fallback to behavior/category
  - fallback to popular/cheap products
- Add `source="lstm"` in recommendation logs.
- Include `sources`/`reasons` in payload for transparency.

### Testing/Validation Tasks

- Generate a demo CSV with at least 500 behavior rows.
- Unit test sequence generation.
- Unit test fallback behavior when no trained model exists.
- Smoke test training command on synthetic/demo data.
- Smoke test inference endpoint after training.

## Phase 4: Cross-Service Integration

- Run migrations for Product Service and AI Service.
- Reseed product data.
- Sync products into AI Service.
- Rebuild embeddings.
- Seed or track behavior events.
- Train LSTM.
- Verify nginx gateway routes all relevant endpoints.
- Verify frontend product browsing still works with typed product payloads.
- Update README with:
  - product inheritance overview
  - nginx gateway usage
  - LSTM training and inference commands

## Open Questions

1. Should `ProductAttribute` / `ProductAttributeValue` remain available for extra flexible metadata, or should they be removed now that each product type has explicit fields?
2. Should frontend display all type-specific fields, or only expose them through API for now?

## Suggested Phase Order

1. Product model inheritance and seed data.
2. Product API serializer/export compatibility.
3. Nginx gateway swap while preserving port `8000`.
4. AI product sync update for `product_type` and type-specific fields.
5. LSTM dataset, training command, and model artifact storage.
6. LSTM inference endpoint and integration into home recommendations.
7. End-to-end smoke test and README update.
