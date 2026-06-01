# Progress

Last updated: 2026-06-01

## Current milestone

M1 - Docker Compose chạy database + skeleton service.

## Completed

- Initialized Git repository locally.
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

## In progress

- First local Git commit for M1 skeleton.

## Next steps

1. Commit M1 skeleton locally.
2. Add User Service domain models, serializers, JWT utilities, auth middleware, and auth/address APIs.
3. Ask for GitHub remote URL or GitHub CLI authorization before first push.

## Open questions

- GitHub remote URL is not configured yet. Local commits can continue; pushing requires a remote.
