# Progress

Last updated: 2026-06-01

## Current milestone

M2 - User/Auth service.

## Completed

- Initialized Git repository locally.
- Created first local commit: `5f368cb chore: scaffold microservices skeleton`.
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

## In progress

- M2 local commit for User/Auth.

## Next steps

1. Commit M2 User/Auth locally.
2. Add Staff Service domain models, serializers, CRUD APIs, seed role command, and migrations.
3. Ask for GitHub remote URL or GitHub CLI authorization before first push.

## Open questions

- GitHub remote URL is not configured yet. Local commits can continue; pushing requires a remote.
