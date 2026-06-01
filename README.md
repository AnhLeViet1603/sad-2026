# E-Commerce Microservices

Hệ thống demo E-Commerce Microservices theo kế hoạch trong `.ai/plan.md`.

## Trạng thái hiện tại

- Đã tạo skeleton cho gateway và 9 service Django/DRF.
- Đã có Docker Compose cho PostgreSQL + pgvector, MySQL, Neo4j và toàn bộ service.
- Mỗi service có endpoint `GET /health`.
- Tiến độ chi tiết được ghi ở `.ai/progress.md`.

## Chạy local bằng Docker

```bash
cp .env.example .env
docker compose up --build
```

Các endpoint chính:

- Gateway: http://localhost:8000/health
- User Service: http://localhost:8001/health
- Staff Service: http://localhost:8002/health
- Product Service: http://localhost:8003/health
- Cart Service: http://localhost:8004/health
- Order Service: http://localhost:8005/health
- Payment Service: http://localhost:8006/health
- Shipping Service: http://localhost:8007/health
- Comment Service: http://localhost:8008/health
- AI Service: http://localhost:8009/health
- Neo4j Browser: http://localhost:7474

