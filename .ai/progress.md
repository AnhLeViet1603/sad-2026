# Progress

Last updated: 2026-06-02

## Current milestone

M10 - Modern ecommerce UI and purchased graph demo.

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
- Added product detail UI view with detail fetch, VIEWED tracking, rating summary, reviews, related products, add-to-cart, and review form.
- Added admin UI control to rebuild AI embeddings.
- Added Gemini environment placeholders to local `.env` and `.env.example`.
- Reworked Docker build setup around a shared multi-target backend Dockerfile.
- Split backend Python dependencies into common, MySQL, Postgres, and AI requirement layers so sibling service images can reuse cache.
- Switched backend runtime to `python:3.12-slim` without per-service apt installs.
- Switched frontend Dockerfile to a Vite build stage plus `nginx:1.27-alpine` runtime.
- Added `.dockerignore`, shared backend startup script, frontend nginx config, and database init scripts.
- Added per-service database names and init scripts for MySQL/Postgres service databases.
- Added hyphenated Docker network aliases and service URLs to avoid Django host validation issues from underscore service names.
- Fixed MySQL compatibility for `RefreshToken.token` by using a bounded unique `CharField`.
- Added `jti` to refresh JWT payloads to prevent duplicate token values when issuing multiple refresh tokens in the same second.
- Verified Docker Compose config with `docker compose config --quiet`.
- Verified full Docker build with shared dependency cache reuse.
- Verified all containers start and remain up through `docker compose up -d --build`.
- Verified backend health endpoints on ports 8000-8009 and frontend on port 3000.
- Seeded 30 demo products from inside `product_service`.
- Verified gateway end-to-end flow: register, login, profile, product list, add cart item, AI behavior tracking, checkout, payment success simulation, review creation, AI product sync, recommendations, and chat.
- Added a focused plan for the next UI/graph iteration in `.ai/plan-ui-purchased.md`.
- Redesigned the frontend into a more modern ecommerce storefront with top navigation, search, category chips, product rails, product detail, cart, checkout, orders, assistant, and operations views.
- Wired checkout success to send `PURCHASED` tracking events through the existing `/api/ai/track` endpoint.
- Added Neo4j relationship `count` updates for tracked behavior.
- Updated graph recommendation scoring so `PURCHASED` behavior weighs more than `ADDED_TO_CART`, `RATED`, and `VIEWED`.
- Added `seed_graph_demo` management command in AI Service to seed supported behavior events, including `PURCHASED`.
- Verified Docker frontend production build through `docker compose up -d --build`.
- Verified `seed_graph_demo` creates 160 behavior events across 10 demo users, including 30 `PURCHASED` relationships.
- Verified checkout flow through the gateway creates a `PURCHASED` relationship in Neo4j and returns graph-based recommendations.

## In progress

- Local commit for modern ecommerce UI and purchased graph demo changes.

## Next steps

1. Run a manual browser smoke test through the frontend at `http://localhost:3000`.
2. Commit modern ecommerce UI and purchased graph demo changes locally.
3. Ask for GitHub remote URL or GitHub CLI authorization before first push.

## Open questions

- GitHub remote URL is not configured yet. Local commits can continue; pushing requires a remote.
