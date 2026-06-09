# SAD 2026 - E-Commerce Microservices

Dự án demo hệ thống thương mại điện tử theo kiến trúc microservices. Backend gồm nhiều service Django/DRF, API Gateway, PostgreSQL + pgvector, MySQL, Neo4j và AI service cho tìm kiếm/gợi ý sản phẩm. Frontend dùng React + Vite.

## Kiến trúc

| Thành phần | Công nghệ | Port local |
| --- | --- | --- |
| Frontend | React, Vite, Nginx | `3000` |
| API Gateway | Nginx reverse proxy | `8000` |
| User Service | Django/DRF, MySQL | `8001` |
| Staff Service | Django/DRF, MySQL | `8002` |
| Product Service | Django/DRF, PostgreSQL | `8003` |
| Cart Service | Django/DRF, PostgreSQL | `8004` |
| Order Service | Django/DRF, PostgreSQL | `8005` |
| Payment Service | Django/DRF, MySQL | `8006` |
| Shipping Service | Django/DRF, MySQL | `8007` |
| Comment Service | Django/DRF, PostgreSQL | `8008` |
| AI Service | Django/DRF, pgvector, Neo4j, Gemini tùy chọn | `8009` |
| PostgreSQL | `pgvector/pgvector:pg16` | `5432` |
| MySQL | `mysql:8.4` | `3306` |
| Neo4j Browser | `neo4j:5` | `17474` |

## Yêu cầu

- Docker Desktop hoặc Docker Engine có Docker Compose.
- Git.
- Tùy chọn: Google Gemini API key để AI service dùng Gemini cho chat và embedding. Nếu không cấu hình `GEMINI_API_KEY`, service sẽ dùng embedding deterministic nội bộ để demo vẫn chạy được.

## Cấu hình môi trường

Tạo file `.env` từ mẫu:

```bash
cp .env.example .env
```

Các biến quan trọng:

- `DJANGO_SECRET_KEY`, `JWT_SECRET`: khóa dùng cho Django/JWT.
- `POSTGRES_*`, `MYSQL_*`: cấu hình database trong Docker Compose.
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: cấu hình Neo4j cho graph recommendation.
- `NEO4J_HTTP_PORT`: port mở Neo4j Browser ra máy host, mặc định `17474`.
- `GEMINI_API_KEY`: API key Gemini, có thể để trống khi chạy demo offline.
- `GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`: model Gemini dùng cho chat và embedding.
- `*_SERVICE_URL`: URL nội bộ giữa các service trong Docker network.

Không commit file `.env` vì file này chứa cấu hình local và secret.

## Chạy toàn bộ hệ thống bằng Docker

Build và chạy toàn bộ service:

```bash
docker compose up --build
```

Các container backend tự chạy migration khi khởi động thông qua `docker/scripts/start-backend.sh`.

Chạy nền:

```bash
docker compose up -d --build
```

Dừng hệ thống:

```bash
docker compose down
```

Dừng và xóa volume database local:

```bash
docker compose down -v
```

## Kiểm tra health check

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
curl http://localhost:8005/health
curl http://localhost:8006/health
curl http://localhost:8007/health
curl http://localhost:8008/health
curl http://localhost:8009/health
```

Truy cập UI:

- Frontend: <http://localhost:3000>
- API Gateway: <http://localhost:8000>
- Neo4j Browser: <http://localhost:17474>

## Seed dữ liệu demo

Sau khi các container đã chạy, seed catalog sản phẩm demo vào Product Service:

```bash
docker compose exec product_service python manage.py seed_products
```

Kiểm tra danh sách sản phẩm:

```bash
curl http://localhost:8000/api/products
```

Gateway sẽ proxy request `/api/products` sang Product Service. Có thể gọi trực tiếp Product Service tại `http://localhost:8003/api/products` khi cần debug.

## Sync product sang AI service

AI service không đọc trực tiếp bảng sản phẩm của Product Service. Sau khi seed hoặc cập nhật catalog, cần sync sản phẩm sang bảng `ProductDocument` của AI service:

```bash
curl -X POST http://localhost:8000/api/ai/sync-products
```

Hoặc gọi trực tiếp AI service:

```bash
curl -X POST http://localhost:8009/api/ai/sync-products
```

Luồng sync:

1. AI service gọi Product Service qua `PRODUCT_SERVICE_URL`.
2. Product Service export catalog active từ endpoint `/api/products/ai/export`.
3. AI service lưu/cập nhật `ProductDocument`.
4. AI service upsert node `Product` và quan hệ category vào Neo4j.
5. Sản phẩm không còn trong catalog export sẽ bị xóa khỏi AI service và Neo4j.

Response thành công có dạng:

```json
{
  "success": true,
  "message": "Products synced",
  "data": {
    "synced": 24
  }
}
```

## Rebuild embedding cho AI service

Sau khi sync product, rebuild embedding để hybrid search và chatbot có dữ liệu vector:

```bash
curl -X POST http://localhost:8000/api/ai/rebuild-embeddings
```

Hoặc gọi trực tiếp AI service:

```bash
curl -X POST http://localhost:8009/api/ai/rebuild-embeddings
```

Ghi chú:

- Nếu `.env` có `GEMINI_API_KEY`, AI service gọi Gemini embedding API với model trong `GEMINI_EMBEDDING_MODEL`.
- Nếu không có `GEMINI_API_KEY` hoặc Gemini lỗi tạm thời, service tự fallback sang deterministic embedding để demo vẫn hoạt động.
- Vector embedding của AI service dùng dimension `3072` và lưu bằng pgvector.

Response thành công có dạng:

```json
{
  "success": true,
  "message": "Embeddings rebuilt",
  "data": {
    "embedded": 24
  }
}
```

## Quy trình khởi tạo dữ liệu khuyến nghị

Chạy theo thứ tự sau sau khi `docker compose up` hoàn tất:

```bash
docker compose exec product_service python manage.py seed_products
curl -X POST http://localhost:8000/api/ai/sync-products
curl -X POST http://localhost:8000/api/ai/rebuild-embeddings
```

Tùy chọn seed hành vi demo cho Neo4j graph recommendation:

```bash
docker compose exec ai_service python manage.py seed_graph_demo
```

Train optional PyTorch LSTM recommendations from the bundled demo add-to-cart CSV:

```bash
docker compose exec ai_service python manage.py train_lstm_recommender \
  --csv chatbot/ml/demo_cart_behavior.csv \
  --epochs 8
```

The CSV contains 560 `ADDED_TO_CART` behavior rows. The trained model artifact is saved to `AI_MODEL_DIR` or `/app/models` by default. Existing AI chat, product sync, and embedding rebuild continue to work without the LSTM artifact; LSTM recommendations are used only when a trained artifact is available.

## API chính

Tất cả endpoint có thể đi qua API Gateway tại `http://localhost:8000`.

Product:

- `GET /api/products`
- `POST /api/products`
- `GET /api/products/search?q=...`
- `GET /api/products/{product_id}`
- `PATCH /api/products/{product_id}`
- `DELETE /api/products/{product_id}`
- `GET /api/products/{product_id}/related`
- `GET /api/products/{product_id}/inventory`
- `PATCH /api/products/{product_id}/inventory`
- `GET /api/products/categories`
- `POST /api/products/categories`

AI:

- `POST /api/ai/sync-products`
- `POST /api/ai/rebuild-embeddings`
- `GET /api/ai/search?q=...`
- `GET /api/ai/recommendations/home`
- `GET /api/ai/recommendations/lstm`
- `POST /api/ai/chat`
- `POST /api/ai/track`

Ví dụ chat:

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Gợi ý sản phẩm để tập thể dục ở nhà\"}"
```

## Phát triển frontend

Chạy frontend qua Docker ở `http://localhost:3000`:

```bash
docker compose up frontend
```

Nếu muốn chạy frontend trực tiếp bằng Node:

```bash
cd frontend
npm install
npm run dev
```

Khi chạy trực tiếp, đảm bảo API base URL trỏ về Gateway `http://localhost:8000`.

## Lệnh hữu ích

Xem log một service:

```bash
docker compose logs -f ai_service
docker compose logs -f product_service
```

Chạy migration thủ công nếu cần:

```bash
docker compose exec product_service python manage.py migrate
docker compose exec ai_service python manage.py migrate
```

Mở Django shell:

```bash
docker compose exec ai_service python manage.py shell
```

## Troubleshooting

- Nếu `sync-products` trả `PRODUCT_SERVICE_ERROR`, kiểm tra `product_service` đã healthy chưa và `PRODUCT_SERVICE_URL` trong `.env`.
- Nếu `rebuild-embeddings` chạy chậm, kiểm tra `GEMINI_API_KEY`; gọi Gemini thật sẽ phụ thuộc mạng và quota API.
- Nếu Neo4j Browser không mở ở `7474`, dùng port host `17474` theo cấu hình mặc định của dự án.
- Nếu muốn làm sạch dữ liệu local hoàn toàn, chạy `docker compose down -v` rồi khởi động lại và seed lại dữ liệu.
