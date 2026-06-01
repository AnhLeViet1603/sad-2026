# Progress

Last updated: 2026-06-01

## Current milestone

M6 - Payment/Shipping then Order checkout.

## Completed

- Initialized Git repository locally.
- Created first local commit: `5f368cb chore: scaffold microservices skeleton`.
- Created second local commit: `73937d5 feat: add user auth service APIs`.
- Created third local commit: `0ed0e13 feat: add staff management APIs`.
- Created fourth local commit: `60088f3 feat: add product catalog APIs`.
- Created fifth local commit: `eef732d feat: add cart service APIs`.
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

## In progress

- Payment and Shipping service skeleton domain APIs.

## Next steps

1. Add Payment and Shipping service skeleton domain APIs to unblock checkout integration.
2. Add Order Service checkout flow.
3. Add Comment Service review APIs.
4. Ask for GitHub remote URL or GitHub CLI authorization before first push.

## Open questions

- GitHub remote URL is not configured yet. Local commits can continue; pushing requires a remote.
