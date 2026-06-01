# Progress

Last updated: 2026-06-01

## Current milestone

M8 - Frontend demo UI.

## Completed

- Initialized Git repository locally.
- Created first local commit: `5f368cb chore: scaffold microservices skeleton`.
- Created second local commit: `73937d5 feat: add user auth service APIs`.
- Created third local commit: `0ed0e13 feat: add staff management APIs`.
- Created fourth local commit: `60088f3 feat: add product catalog APIs`.
- Created fifth local commit: `eef732d feat: add cart service APIs`.
- Created sixth local commit: `0a62382 docs: update progress after cart service`.
- Created seventh local commit: `9e45258 feat: add demo payment and shipping APIs`.
- Created eighth local commit: `e1d89e0 feat: add order checkout flow`.
- Created ninth local commit: `433f54e feat: add product review APIs`.
- Created tenth local commit: `ab3fb07 feat: add demo ai recommendation APIs`.
- Created eleventh local commit: `e33f175 feat: add api gateway proxy routes`.
- Created twelfth local commit: `e8bc9d3 feat: add frontend demo UI`.
- Created thirteenth local commit: `2e5886d docs: note pending runtime verification`.
- Created project structure for:
  - `api_gateway`
  - `user_service`
  - `staff_service`
  - `product_service`
  - `cart_service`
  - `order_service`
  - `payment_service`
  - `shipping_service`
  - `comment_service`
  - `ai_service`
  - `frontend`
- Added shared Django settings and response helpers in `common/`.
- Added `.env.example`, `.gitignore`, `docker-compose.yml`, and `README.md`.
- Added Django skeleton files, Dockerfiles, requirements, and `/health` endpoints for all backend services.
- Created local `.env` from `.env.example` for Docker Compose usage. The `.env` file is ignored by Git.
- Verified Python syntax with `python -m compileall`.
- Verified Docker Compose shape with `docker compose config`.
- Added shared JWT utilities and request middleware.
- Added User Service models: `User`, `Address`, `RefreshToken`.
- Added User Service serializers, auth/profile/address views, routes, and initial migration.
- Added Staff Service models, serializers, CRUD views, routes, initial migration, and `seed_roles` command.
- Verified Staff Service syntax with `python -m compileall`.
- Added Product Service models for category, product, image, inventory, dynamic attributes, and pgvector embedding.
- Added Product Service serializers, CRUD/search/related/inventory/category/export APIs, migration, and `seed_products` command.
- Verified Product Service syntax with `python -m compileall`.
- Added Cart Service models, serializers, Product Service validation client, cart APIs, and initial migration.
- Verified Cart Service syntax with `python -m compileall`.
- Added demo-only Payment Service models, serializers, create/list/detail/simulate/callback APIs, and migration.
- Added demo-only Shipping Service models, serializers, fee/create/list/detail/tracking/status APIs, and migration.
- Verified Payment and Shipping syntax with `python -m compileall`.
- Added Order Service models, serializers, checkout orchestration, list/detail/status APIs, and migration.
- Order checkout now calls Cart, Payment, and Shipping services and clears the cart after successful orchestration.
- Verified Order Service syntax with `python -m compileall`.
- Added Comment Service review/reply models, serializers, review list/create, product reviews, rating summary, reply APIs, and migration.
- Verified Comment Service syntax with `python -m compileall`.
- Added AI Service demo models, product sync, behavior tracking, home recommendations, and mock chatbot APIs.
- Verified AI Service syntax with `python -m compileall`.
- Added API Gateway proxy routing for `/api/users`, `/api/staff`, `/api/products`, `/api/cart`, `/api/orders`, `/api/payments`, `/api/shipping`, `/api/comments`, and `/api/ai`.
- Gateway forwards authorization and derived user headers.
- Verified API Gateway syntax with `python -m compileall`.
- Added React/Vite frontend demo with shop, auth, cart, checkout, orders, AI/review, and admin panels.
- Added frontend Dockerfile and Docker Compose service on port 3000.
- Re-ran full Python syntax check and Docker Compose config after frontend changes.
- Attempted `docker compose build api_gateway`; blocked by Docker access to `C:\Users\hoang\.docker\buildx\instances`. Escalated build permission was not granted, so runtime verification is still pending.
- Added Gemini API environment variables for generation and embeddings.
- Added true demo RAG plumbing: product documents, Gemini/fallback embeddings, pgvector vector search, hybrid retrieval, and Gemini grounded response generation.
- Added Neo4j graph upsert/tracking and graph-based home recommendation fallback path.
- Added AI endpoints: `/api/ai/rebuild-embeddings` and `/api/ai/search`.

## In progress

- Product detail UI and AI admin controls.

## Next steps

1. Add product detail UI.
2. Add admin controls for AI product sync and embedding rebuild.
3. Commit Gemini/RAG/Neo4j/detail changes locally.
4. Run `docker compose up --build` when Docker permission is available.
5. Run migrations and seed commands in containers.
6. Test the customer/admin demo flow through the frontend.
7. Ask for GitHub remote URL or GitHub CLI authorization before first push.

## Open questions

- GitHub remote URL is not configured yet. Local commits can continue; pushing requires a remote.
