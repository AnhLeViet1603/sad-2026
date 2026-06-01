# PLAN.md — Kế hoạch xây dựng hệ thống E-Commerce Microservices giống báo cáo

> Mục tiêu: xây dựng một hệ thống E-Commerce Microservices theo đúng định hướng trong báo cáo: dùng Django + Django REST Framework cho các microservice, JWT custom, PostgreSQL + pgvector, MySQL, Neo4j, Docker Compose, API Gateway, AI Service tư vấn sản phẩm, RAG, Hybrid Retrieval, Knowledge Graph và giao diện quản trị/khách hàng.

---

## 1. Phạm vi hệ thống

### 1.1. Hệ thống cần xây dựng

Hệ thống là một nền tảng thương mại điện tử có các nhóm chức năng chính:

1. Quản lý người dùng.
2. Quản lý nhân viên, vai trò, quyền hạn.
3. Quản lý sản phẩm, danh mục, thuộc tính động.
4. Quản lý giỏ hàng.
5. Quản lý đơn hàng.
6. Quản lý thanh toán.
7. Quản lý vận chuyển.
8. Quản lý đánh giá, bình luận sản phẩm.
9. Theo dõi hành vi người dùng.
10. Tư vấn sản phẩm bằng AI Chatbot.
11. Gợi ý sản phẩm bằng RAG + Knowledge Graph.
12. Giao diện quản trị và dashboard vận hành.
13. Triển khai toàn bộ bằng Docker Compose.

### 1.2. Mục tiêu demo cuối cùng

Luồng demo bắt buộc phải chạy được:

```text
Khách hàng đăng ký/đăng nhập
 -> xem danh sách sản phẩm
 -> xem chi tiết sản phẩm
 -> thêm vào giỏ hàng
 -> tạo đơn hàng
 -> thanh toán giả lập
 -> tạo thông tin vận chuyển
 -> xem trạng thái đơn hàng
 -> đánh giá sản phẩm
 -> chatbot tư vấn sản phẩm
 -> hệ thống gợi ý sản phẩm liên quan
```

Luồng admin/staff bắt buộc phải chạy được:

```text
Staff/Admin đăng nhập
 -> quản lý sản phẩm
 -> quản lý danh mục
 -> quản lý đơn hàng
 -> cập nhật trạng thái đơn hàng
 -> xem dashboard đơn giản
```

---

## 2. Tech stack giữ đúng theo báo cáo

### 2.1. Backend

Tất cả microservice chính dùng:

```text
Python
Django
Django REST Framework
Django ORM
JWT custom
```

Không đổi sang Spring Boot, FastAPI cho core service, NestJS hoặc framework khác.

### 2.2. Database

Hệ thống dùng phối hợp nhiều CSDL:

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Product/Order/AI vector | PostgreSQL + pgvector | Lưu sản phẩm, đơn hàng, embedding/vector phục vụ AI |
| User/Payment/Shipping | MySQL | Lưu người dùng, thanh toán, vận chuyển |
| Knowledge Graph | Neo4j | Lưu quan hệ người dùng - sản phẩm - danh mục - hành vi |
| Cache tùy chọn | Redis | Cache session, token blacklist, cache product/search nếu cần |

### 2.3. AI/RAG

AI Service sử dụng:

```text
Python
Django hoặc Django REST Framework nếu muốn đồng bộ stack
PostgreSQL + pgvector
Neo4j
Embedding model
Hybrid Retrieval
RAG pipeline
LLM integration hoặc mock LLM ở bản demo
```

### 2.4. Infrastructure

```text
Docker
Docker Compose
API Gateway / Reverse Proxy
JWT custom auth
```

API Gateway có thể triển khai bằng một trong hai hướng:

1. Django API Gateway service tự viết bằng DRF + requests/httpx.
2. Nginx reverse proxy route theo path.

Để giống báo cáo hơn, nên có thư mục `api_gateway` riêng và cấu hình route/proxy rõ ràng.

---

## 3. Kiến trúc tổng thể

### 3.1. Sơ đồ logic

```text
[Client Web / Admin UI]
          |
          v
[API Gateway]
          |
          +--> [User Service] ---------> MySQL
          |
          +--> [Staff Service] --------> MySQL
          |
          +--> [Product Service] ------> PostgreSQL + pgvector
          |
          +--> [Cart Service] ---------> PostgreSQL hoặc MySQL
          |
          +--> [Order Service] --------> PostgreSQL
          |
          +--> [Payment Service] ------> MySQL
          |
          +--> [Shipping Service] -----> MySQL
          |
          +--> [Comment Service] ------> PostgreSQL
          |
          +--> [AI Service] -----------> PostgreSQL + pgvector
                                      \-> Neo4j
```

### 3.2. Nguyên tắc thiết kế

1. Mỗi service sở hữu domain nghiệp vụ riêng.
2. Mỗi service có database/schema riêng.
3. Service không truy vấn trực tiếp database của service khác.
4. Giao tiếp giữa service thông qua REST API.
5. API Gateway là điểm vào duy nhất từ client.
6. JWT được dùng xuyên suốt để xác thực.
7. Product/Order/AI là các domain quan trọng nhất của hệ thống.
8. AI Service không thay thế Product Service, chỉ đọc dữ liệu sản phẩm qua API hoặc bản đồng bộ riêng.
9. Các lỗi liên service phải có fallback tối thiểu.
10. Docker Compose phải chạy được toàn bộ hệ thống bằng một lệnh.

---

## 4. Phân rã bounded context và microservice

### 4.1. User Context -> User Service

Trách nhiệm:

- Đăng ký tài khoản.
- Đăng nhập.
- Quản lý hồ sơ người dùng.
- Quản lý địa chỉ giao hàng của người dùng.
- Phát hành JWT.
- Xác thực token.

Entity chính:

```text
User
Address
UserProfile
RefreshToken / TokenBlacklist
```

Database đề xuất: MySQL.

### 4.2. Staff Context -> Staff Service

Trách nhiệm:

- Quản lý nhân viên.
- Quản lý phòng ban.
- Quản lý role.
- Quản lý permission.
- Phân quyền quản trị.

Entity chính:

```text
Staff
Role
Permission
Department
StaffRole
RolePermission
```

Database đề xuất: MySQL.

### 4.3. Product Context -> Product Service

Trách nhiệm:

- Quản lý sản phẩm.
- Quản lý danh mục.
- Quản lý tồn kho.
- Quản lý thuộc tính động.
- Cung cấp API tìm kiếm/lọc sản phẩm.
- Cung cấp dữ liệu cho AI Service.

Entity chính:

```text
Product
Category
ProductImage
ProductAttribute
ProductAttributeValue
Inventory
ProductEmbedding
```

Database đề xuất: PostgreSQL + pgvector.

### 4.4. Cart Context -> Cart Service

Trách nhiệm:

- Tạo giỏ hàng cho người dùng.
- Thêm sản phẩm vào giỏ.
- Cập nhật số lượng.
- Xóa sản phẩm khỏi giỏ.
- Lấy tổng tiền tạm tính.
- Chuẩn bị dữ liệu checkout.

Entity chính:

```text
Cart
CartItem
```

Database đề xuất: PostgreSQL hoặc MySQL.

### 4.5. Order Context -> Order Service

Trách nhiệm:

- Tạo đơn hàng từ giỏ hàng.
- Lưu snapshot sản phẩm tại thời điểm mua.
- Quản lý trạng thái đơn hàng.
- Tính tổng tiền.
- Phối hợp với Payment Service và Shipping Service.

Entity chính:

```text
Order
OrderItem
OrderStatusHistory
```

Database đề xuất: PostgreSQL.

### 4.6. Payment Context -> Payment Service

Trách nhiệm:

- Tạo giao dịch thanh toán.
- Giả lập thanh toán.
- Cập nhật trạng thái thanh toán.
- Lưu lịch sử thanh toán.
- Cung cấp kết quả thanh toán cho Order Service.

Entity chính:

```text
Payment
PaymentTransaction
PaymentMethod
```

Database đề xuất: MySQL.

### 4.7. Shipping Context -> Shipping Service

Trách nhiệm:

- Tạo yêu cầu vận chuyển.
- Lưu địa chỉ giao hàng.
- Cập nhật trạng thái vận chuyển.
- Tính phí vận chuyển giả lập.
- Theo dõi tracking code.

Entity chính:

```text
Shipping
Shipment
ShippingAddress
ShippingStatusHistory
```

Database đề xuất: MySQL.

### 4.8. Comment/Review Context -> Comment Service

Trách nhiệm:

- Người dùng đánh giá sản phẩm.
- Người dùng bình luận sản phẩm.
- Hỗ trợ reply/comment đa cấp nếu cần.
- Tính rating trung bình.
- Cung cấp dữ liệu review cho AI Service.

Entity chính:

```text
Comment
Review
Rating
CommentReply
```

Database đề xuất: PostgreSQL.

### 4.9. AI Recommendation Context -> AI Service

Trách nhiệm:

- Tư vấn sản phẩm bằng chatbot.
- Lấy dữ liệu sản phẩm.
- Tạo embedding sản phẩm.
- Lưu vector vào PostgreSQL + pgvector.
- Lưu quan hệ người dùng - sản phẩm - danh mục vào Neo4j.
- Hybrid Retrieval: keyword + vector + graph.
- Sinh câu trả lời tư vấn sản phẩm.
- Gợi ý sản phẩm trên trang chủ.

Entity/bảng chính:

```text
ProductDocument
ProductVector
UserBehavior
RecommendationLog
ChatSession
ChatMessage
```

Neo4j node/relationship:

```text
(:User)
(:Product)
(:Category)
(:Brand)

(:User)-[:VIEWED]->(:Product)
(:User)-[:ADDED_TO_CART]->(:Product)
(:User)-[:PURCHASED]->(:Product)
(:User)-[:RATED]->(:Product)
(:Product)-[:IN_CATEGORY]->(:Category)
(:Product)-[:SIMILAR_TO]->(:Product)
```

---

## 5. Cấu trúc thư mục dự án

```text
ecom-final/
│
├── api_gateway/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── gateway/
│   └── routes/
│
├── user_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── user_service/
│   └── users/
│
├── staff_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── staff_service/
│   └── staff/
│
├── product_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── product_service/
│   └── products/
│
├── cart_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── cart_service/
│   └── carts/
│
├── order_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── order_service/
│   └── orders/
│
├── payment_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── payment_service/
│   └── payments/
│
├── shipping_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── shipping_service/
│   └── shipping/
│
├── comment_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── comment_service/
│   └── comments/
│
├── ai_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── ai_service/
│   ├── chatbot/
│   ├── rag/
│   ├── embeddings/
│   ├── graph/
│   └── recommend/
│
├── frontend/
│   ├── package.json
│   ├── src/
│   └── Dockerfile
│
├── docker-compose.yml
├── .env
├── README.md
└── PLAN.md
```

---

## 6. API Gateway plan

### 6.1. Route mapping

```text
/api/users/**       -> user_service:8001
/api/staff/**       -> staff_service:8002
/api/products/**    -> product_service:8003
/api/cart/**        -> cart_service:8004
/api/orders/**      -> order_service:8005
/api/payments/**    -> payment_service:8006
/api/shipping/**    -> shipping_service:8007
/api/comments/**    -> comment_service:8008
/api/ai/**          -> ai_service:8009
```

### 6.2. Nhiệm vụ Gateway

- Nhận request từ frontend.
- Verify JWT ở mức gateway nếu có thể.
- Forward request đến service tương ứng.
- Gắn header `X-User-Id`, `X-User-Role` sau khi verify token.
- Chuẩn hóa response lỗi.
- Cấu hình CORS.
- Ghi access log.

### 6.3. Endpoint gateway

```text
GET  /health
ANY  /api/users/*
ANY  /api/staff/*
ANY  /api/products/*
ANY  /api/cart/*
ANY  /api/orders/*
ANY  /api/payments/*
ANY  /api/shipping/*
ANY  /api/comments/*
ANY  /api/ai/*
```

---

## 7. Thiết kế chi tiết từng service

## 7.1. User Service

### Chức năng

- Register.
- Login.
- Refresh token.
- Logout.
- Get profile.
- Update profile.
- CRUD address.

### API

```text
POST   /api/users/register
POST   /api/users/login
POST   /api/users/refresh
POST   /api/users/logout
GET    /api/users/me
PATCH  /api/users/me
GET    /api/users/addresses
POST   /api/users/addresses
PATCH  /api/users/addresses/{id}
DELETE /api/users/addresses/{id}
GET    /api/users/verify-token
```

### Model

```python
class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Address(models.Model):
    user_id = models.BigIntegerField()
    receiver_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    detail = models.TextField()
    is_default = models.BooleanField(default=False)
```

---

## 7.2. Staff Service

### Chức năng

- Quản lý staff.
- Quản lý role.
- Quản lý permission.
- Quản lý department.
- Kiểm tra quyền admin/staff.

### API

```text
GET    /api/staff
POST   /api/staff
GET    /api/staff/{id}
PATCH  /api/staff/{id}
DELETE /api/staff/{id}

GET    /api/staff/roles
POST   /api/staff/roles
PATCH  /api/staff/roles/{id}
DELETE /api/staff/roles/{id}

GET    /api/staff/permissions
POST   /api/staff/permissions

GET    /api/staff/departments
POST   /api/staff/departments
```

### Model

```python
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(Permission)

class Staff(models.Model):
    user_id = models.BigIntegerField()
    employee_code = models.CharField(max_length=50, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    roles = models.ManyToManyField(Role)
    is_active = models.BooleanField(default=True)
```

---

## 7.3. Product Service

### Chức năng

- CRUD sản phẩm.
- CRUD danh mục.
- Upload/lưu ảnh sản phẩm.
- Quản lý tồn kho.
- Tìm kiếm/lọc sản phẩm.
- API phục vụ AI sync dữ liệu.
- Lưu embedding sản phẩm với pgvector.

### API

```text
GET    /api/products
POST   /api/products
GET    /api/products/{id}
PATCH  /api/products/{id}
DELETE /api/products/{id}

GET    /api/products/search?q=&category=&min_price=&max_price=
GET    /api/products/{id}/related
GET    /api/products/{id}/inventory
PATCH  /api/products/{id}/inventory

GET    /api/products/categories
POST   /api/products/categories
PATCH  /api/products/categories/{id}
DELETE /api/products/categories/{id}

GET    /api/products/ai/export
POST   /api/products/ai/embedding/{id}
```

### Model

```python
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent_id = models.BigIntegerField(null=True, blank=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=30, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.TextField()
    is_thumbnail = models.BooleanField(default=False)

class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

class ProductAttribute(models.Model):
    name = models.CharField(max_length=100)

class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.TextField()
```

### pgvector extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE product_embedding (
    id BIGSERIAL PRIMARY KEY,
    product_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7.4. Cart Service

### Chức năng

- Lấy giỏ hàng hiện tại.
- Thêm sản phẩm vào giỏ.
- Cập nhật số lượng.
- Xóa item.
- Xóa toàn bộ giỏ.
- Validate giỏ trước checkout.

### API

```text
GET    /api/cart
POST   /api/cart/items
PATCH  /api/cart/items/{id}
DELETE /api/cart/items/{id}
DELETE /api/cart/clear
POST   /api/cart/validate
```

### Model

```python
class Cart(models.Model):
    user_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
```

### Lưu ý

Cart Service không query trực tiếp Product DB. Khi thêm sản phẩm, Cart Service gọi Product Service để lấy:

```text
product_id
name
price
stock
status
```

---

## 7.5. Order Service

### Chức năng

- Tạo đơn hàng từ cart.
- Lấy danh sách đơn hàng của user.
- Lấy chi tiết đơn hàng.
- Staff cập nhật trạng thái đơn hàng.
- Lưu snapshot order item.
- Gọi Payment Service tạo payment.
- Gọi Shipping Service tạo shipment.

### API

```text
POST   /api/orders/checkout
GET    /api/orders/my
GET    /api/orders/{id}
GET    /api/orders
PATCH  /api/orders/{id}/status
POST   /api/orders/{id}/cancel
```

### Model

```python
class Order(models.Model):
    user_id = models.BigIntegerField()
    status = models.CharField(max_length=30, default="PENDING")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=30, default="UNPAID")
    shipping_status = models.CharField(max_length=30, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.BigIntegerField()
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=30, null=True)
    new_status = models.CharField(max_length=30)
    changed_by = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Order status

```text
PENDING
CONFIRMED
PAID
PACKING
SHIPPING
COMPLETED
CANCELLED
FAILED
```

---

## 7.6. Payment Service

### Chức năng

- Tạo payment cho order.
- Giả lập thanh toán thành công/thất bại.
- Lấy trạng thái payment.
- Callback/cập nhật payment.
- Lưu transaction.

### API

```text
POST   /api/payments
GET    /api/payments/{id}
GET    /api/payments/order/{order_id}
POST   /api/payments/{id}/simulate-success
POST   /api/payments/{id}/simulate-failed
POST   /api/payments/callback
```

### Model

```python
class Payment(models.Model):
    order_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=30, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentTransaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    transaction_code = models.CharField(max_length=100, unique=True)
    provider = models.CharField(max_length=50, default="MOCK")
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 7.7. Shipping Service

### Chức năng

- Tạo shipment cho order.
- Tính phí vận chuyển giả lập.
- Cập nhật trạng thái vận chuyển.
- Lấy tracking info.
- Lưu địa chỉ giao hàng.

### API

```text
POST   /api/shipping
GET    /api/shipping/{id}
GET    /api/shipping/order/{order_id}
POST   /api/shipping/calculate-fee
PATCH  /api/shipping/{id}/status
```

### Model

```python
class Shipment(models.Model):
    order_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    receiver_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address_detail = models.TextField()
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2)
    tracking_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=30, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
```

### Shipping status

```text
CREATED
PICKING
IN_TRANSIT
DELIVERED
FAILED
RETURNED
```

---

## 7.8. Comment Service

### Chức năng

- Tạo review sản phẩm.
- Tạo comment.
- Reply comment.
- Xóa/sửa comment.
- Lấy rating trung bình của sản phẩm.
- Lấy review theo sản phẩm.

### API

```text
GET    /api/comments/product/{product_id}
POST   /api/comments
PATCH  /api/comments/{id}
DELETE /api/comments/{id}

POST   /api/comments/{id}/reply

GET    /api/comments/product/{product_id}/rating-summary
POST   /api/comments/reviews
```

### Model

```python
class Comment(models.Model):
    product_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    parent_id = models.BigIntegerField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    product_id = models.BigIntegerField()
    user_id = models.BigIntegerField()
    rating = models.IntegerField()
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 7.9. AI Service

### Chức năng

- Chatbot tư vấn sản phẩm.
- Gợi ý sản phẩm theo hành vi.
- Gợi ý sản phẩm tương tự.
- Đồng bộ dữ liệu sản phẩm.
- Tạo embedding.
- Lưu vector vào pgvector.
- Lưu graph vào Neo4j.
- Hybrid Retrieval.
- RAG answer generation.

### API

```text
POST   /api/ai/chat
GET    /api/ai/recommendations/home
GET    /api/ai/recommendations/product/{product_id}
POST   /api/ai/track
POST   /api/ai/sync/products
POST   /api/ai/embeddings/rebuild
GET    /api/ai/health
```

### Request chatbot

```json
{
  "user_id": 1,
  "message": "Tôi muốn mua sách lập trình Python cho người mới bắt đầu",
  "session_id": "abc123"
}
```

### Response chatbot

```json
{
  "answer": "Bạn có thể tham khảo các sản phẩm sau...",
  "products": [
    {
      "id": 10,
      "name": "Python cơ bản",
      "price": 120000,
      "reason": "Phù hợp với người mới bắt đầu, có nhiều đánh giá tốt"
    }
  ],
  "retrieval_sources": ["keyword", "vector", "graph"]
}
```

---

## 8. RAG và AI Recommendation plan

### 8.1. Knowledge Base

Nguồn dữ liệu đưa vào AI:

```text
Product name
Product description
Category
Brand
Price range
Attributes
Reviews
User behavior
Purchase history
Cart history
```

### 8.2. Product document format

Mỗi sản phẩm được chuyển thành document:

```text
Tên sản phẩm: ...
Danh mục: ...
Thương hiệu: ...
Giá: ...
Mô tả: ...
Thuộc tính: ...
Đánh giá nổi bật: ...
Phù hợp với: ...
```

### 8.3. Embedding pipeline

```text
Product Service
 -> export product data
 -> AI Service normalize document
 -> embedding model encode
 -> save vector into PostgreSQL pgvector
```

### 8.4. Graph pipeline

```text
User behavior event
 -> AI Service /track
 -> write relationship into Neo4j
 -> use graph query for recommendation
```

### 8.5. Hybrid Retrieval

Khi người dùng hỏi chatbot:

```text
User query
 -> Keyword search trong product document
 -> Vector search bằng pgvector
 -> Graph search bằng Neo4j nếu có user_id
 -> Fusion/rerank kết quả
 -> Build context
 -> Generate answer
```

### 8.6. Fast pipeline

Dùng cho gợi ý nhanh ở trang chủ:

```text
user_id
 -> Neo4j query sản phẩm cùng category với sản phẩm đã xem/mua
 -> fallback popular products
 -> trả về danh sách sản phẩm
```

### 8.7. Full pipeline

Dùng cho chatbot:

```text
message + user_id
 -> intent detection
 -> hybrid retrieval
 -> context construction
 -> LLM/mock LLM
 -> answer + recommended products
```

### 8.8. Neo4j Cypher mẫu

```cypher
MERGE (u:User {id: $user_id})
MERGE (p:Product {id: $product_id})
MERGE (u)-[r:VIEWED]->(p)
ON CREATE SET r.count = 1, r.created_at = datetime()
ON MATCH SET r.count = r.count + 1, r.updated_at = datetime();
```

Gợi ý theo category:

```cypher
MATCH (u:User {id: $user_id})-[:VIEWED|PURCHASED]->(p:Product)-[:IN_CATEGORY]->(c:Category)
MATCH (rec:Product)-[:IN_CATEGORY]->(c)
WHERE NOT (u)-[:PURCHASED]->(rec)
RETURN rec.id AS product_id, count(*) AS score
ORDER BY score DESC
LIMIT 10;
```

---

## 9. Luồng nghiệp vụ tổng thể

### 9.1. Product View & Cart Flow

```text
1. Client gọi GET /api/products.
2. Gateway forward sang Product Service.
3. Product Service trả danh sách sản phẩm.
4. Client gọi GET /api/products/{id}.
5. Client gửi event VIEWED sang /api/ai/track.
6. User bấm thêm vào giỏ.
7. Client gọi POST /api/cart/items.
8. Cart Service gọi Product Service kiểm tra sản phẩm/tồn kho.
9. Cart Service lưu CartItem.
10. AI Service ghi hành vi ADD_TO_CART vào Neo4j.
```

### 9.2. Purchase & Checkout Flow

```text
1. Client gọi POST /api/orders/checkout.
2. Order Service gọi Cart Service lấy cart.
3. Order Service validate cart.
4. Order Service tạo Order + OrderItem.
5. Order Service gọi Payment Service tạo payment.
6. Order Service gọi Shipping Service tạo shipment.
7. Payment Service giả lập thanh toán.
8. Order Service cập nhật payment_status.
9. Cart Service clear cart.
10. AI Service ghi PURCHASED behavior.
```

### 9.3. AI Chatbot Flow

```text
1. User nhập câu hỏi tư vấn.
2. Client gọi POST /api/ai/chat.
3. AI Service phân tích intent.
4. AI Service chạy keyword search.
5. AI Service chạy vector search bằng pgvector.
6. AI Service chạy graph recommendation bằng Neo4j.
7. AI Service fusion kết quả.
8. AI Service tạo câu trả lời.
9. Client hiển thị câu trả lời và sản phẩm gợi ý.
```

### 9.4. Behavior Tracking Flow

```text
1. Client hoặc service gửi event tới AI Service.
2. Event gồm user_id, product_id, action, metadata.
3. AI Service lưu event log.
4. AI Service cập nhật Neo4j relationship.
5. Recommendation dùng dữ liệu này để cá nhân hóa.
```

### 9.5. Product Review Flow

```text
1. User mua hàng xong.
2. User gửi review sản phẩm.
3. Comment Service lưu Review.
4. Product Service có thể lấy rating summary.
5. AI Service sync review để cải thiện tư vấn.
```

---

## 10. Docker Compose plan

### 10.1. Container cần có

```text
api_gateway
user_service
staff_service
product_service
cart_service
order_service
payment_service
shipping_service
comment_service
ai_service
frontend
postgres
mysql
neo4j
redis
```

### 10.2. Port đề xuất

```text
frontend:          3000
api_gateway:       8000
user_service:      8001
staff_service:     8002
product_service:   8003
cart_service:      8004
order_service:     8005
payment_service:   8006
shipping_service:  8007
comment_service:   8008
ai_service:        8009
postgres:          5432
mysql:             3306
neo4j http:        7474
neo4j bolt:        7687
redis:             6379
```

### 10.3. docker-compose skeleton

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: ecom
      POSTGRES_PASSWORD: ecom
      POSTGRES_DB: ecom
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: ecom
      MYSQL_USER: ecom
      MYSQL_PASSWORD: ecom
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api_gateway:
    build: ./api_gateway
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - user_service
      - product_service
      - ai_service

  user_service:
    build: ./user_service
    ports:
      - "8001:8001"
    env_file: .env
    depends_on:
      - mysql

  staff_service:
    build: ./staff_service
    ports:
      - "8002:8002"
    env_file: .env
    depends_on:
      - mysql

  product_service:
    build: ./product_service
    ports:
      - "8003:8003"
    env_file: .env
    depends_on:
      - postgres

  cart_service:
    build: ./cart_service
    ports:
      - "8004:8004"
    env_file: .env
    depends_on:
      - postgres

  order_service:
    build: ./order_service
    ports:
      - "8005:8005"
    env_file: .env
    depends_on:
      - postgres

  payment_service:
    build: ./payment_service
    ports:
      - "8006:8006"
    env_file: .env
    depends_on:
      - mysql

  shipping_service:
    build: ./shipping_service
    ports:
      - "8007:8007"
    env_file: .env
    depends_on:
      - mysql

  comment_service:
    build: ./comment_service
    ports:
      - "8008:8008"
    env_file: .env
    depends_on:
      - postgres

  ai_service:
    build: ./ai_service
    ports:
      - "8009:8009"
    env_file: .env
    depends_on:
      - postgres
      - neo4j

volumes:
  postgres_data:
  mysql_data:
  neo4j_data:
```

---

## 11. Dependencies chuẩn cho Django service

### 11.1. requirements.txt cơ bản

```text
Django>=5.0
djangorestframework
django-cors-headers
PyJWT
requests
python-dotenv
gunicorn
```

### 11.2. Với PostgreSQL service

```text
psycopg2-binary
pgvector
```

### 11.3. Với MySQL service

```text
mysqlclient
```

Nếu `mysqlclient` lỗi trên Windows, dùng:

```text
PyMySQL
```

### 11.4. Với AI Service

```text
sentence-transformers
numpy
scikit-learn
neo4j
psycopg2-binary
pgvector
transformers
torch
```

Nếu máy yếu, bản demo có thể thay embedding model bằng TF-IDF hoặc mock vector trước.

---

## 12. JWT custom plan

### 12.1. jwt_utils.py

Tạo file chung logic JWT ở từng service hoặc shared package copy:

```python
import jwt
import datetime
from django.conf import settings

def create_access_token(user_id, role="USER"):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
```

### 12.2. Middleware

Mỗi service cần middleware:

```text
Authorization: Bearer <token>
 -> decode token
 -> set request.user_id
 -> set request.role
```

Gateway cũng có thể verify trước.

---

## 13. Frontend plan

### 13.1. Công nghệ frontend

Báo cáo không cố định chi tiết frontend, nhưng cần có giao diện:

- Trang khách hàng.
- Trang quản trị.
- Chatbot UI.
- Trang sản phẩm gợi ý.
- Trang checkout.

Có thể dùng:

```text
React
Vite hoặc Next.js
Axios
Tailwind CSS
```

### 13.2. Pages khách hàng

```text
/
/products
/products/:id
/cart
/checkout
/orders
/orders/:id
/chatbot
/login
/register
```

### 13.3. Pages admin/staff

```text
/admin
/admin/products
/admin/orders
/admin/categories
/admin/staff
/admin/dashboard
```

### 13.4. Component chính

```text
ProductCard
ProductList
ProductDetail
CartItem
CheckoutForm
OrderStatusBadge
ChatbotBox
RecommendedProducts
AdminSidebar
DashboardCard
```

---

## 14. Seed data

### 14.1. Product seed

Cần tối thiểu 30 sản phẩm để demo AI.

Nhóm sản phẩm mẫu nếu làm BookStore/E-Commerce sách:

```text
Sách lập trình
Sách AI/Data
Sách kinh tế
Sách ngoại ngữ
Sách kỹ năng
Sách thiếu nhi
```

Mỗi sản phẩm cần:

```text
name
description
price
category
brand/publisher
attributes
stock
image
```

### 14.2. User behavior seed

Tạo dữ liệu hành vi mẫu:

```text
User 1 viewed product 1, 2, 3
User 1 added product 2 to cart
User 1 purchased product 3
User 2 viewed product 3, 4
User 2 purchased product 4
```

### 14.3. Review seed

Mỗi sản phẩm nên có 2-5 review để AI có dữ liệu tư vấn.

---

## 15. Kế hoạch triển khai theo giai đoạn

## Giai đoạn 0 — Chuẩn bị

Thời lượng: 0.5 - 1 ngày.

Checklist:

- Tạo repository `ecom-final`.
- Tạo các thư mục service.
- Tạo `.env`.
- Tạo `docker-compose.yml`.
- Chốt port từng service.
- Chốt database từng service.
- Chốt chuẩn response JSON.

Chuẩn response:

```json
{
  "success": true,
  "data": {},
  "message": "OK"
}
```

Chuẩn error:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input"
  }
}
```

---

## Giai đoạn 1 — Database và service skeleton

Thời lượng: 2 - 3 ngày.

Việc cần làm:

1. Tạo Django project cho từng service.
2. Cấu hình DRF.
3. Cấu hình CORS.
4. Cấu hình database.
5. Tạo Dockerfile cho từng service.
6. Tạo health endpoint:

```text
GET /health
```

Definition of Done:

- `docker compose up` chạy được tất cả service.
- Mỗi service trả được `/health`.
- PostgreSQL, MySQL, Neo4j chạy được.

---

## Giai đoạn 2 — User Service + JWT

Thời lượng: 2 ngày.

Việc cần làm:

1. Tạo User model.
2. Tạo Address model.
3. Register API.
4. Login API.
5. Generate JWT.
6. Verify JWT.
7. Middleware parse token.
8. Test bằng Postman.

Definition of Done:

- Đăng ký thành công.
- Đăng nhập nhận access token.
- Gọi `/api/users/me` bằng token thành công.
- Thêm/sửa/xóa địa chỉ thành công.

---

## Giai đoạn 3 — Staff Service

Thời lượng: 1.5 - 2 ngày.

Việc cần làm:

1. Tạo Department.
2. Tạo Permission.
3. Tạo Role.
4. Tạo Staff.
5. Tạo API CRUD.
6. Tạo seed role:

```text
ADMIN
STAFF
PRODUCT_MANAGER
ORDER_MANAGER
```

Definition of Done:

- Admin tạo được staff.
- Staff có role/permission.
- API kiểm tra role chạy được.

---

## Giai đoạn 4 — Product Service

Thời lượng: 3 - 4 ngày.

Việc cần làm:

1. Tạo Category.
2. Tạo Product.
3. Tạo ProductImage.
4. Tạo Inventory.
5. Tạo ProductAttribute.
6. CRUD sản phẩm.
7. Search/filter sản phẩm.
8. Export API cho AI.
9. Tạo seed 30 sản phẩm.
10. Cài pgvector extension.

Definition of Done:

- Xem danh sách sản phẩm.
- Xem chi tiết sản phẩm.
- Admin tạo/sửa/xóa sản phẩm.
- Search/lọc sản phẩm chạy được.
- AI Service gọi được `/api/products/ai/export`.

---

## Giai đoạn 5 — Cart Service

Thời lượng: 2 ngày.

Việc cần làm:

1. Tạo Cart.
2. Tạo CartItem.
3. Add item.
4. Update quantity.
5. Remove item.
6. Clear cart.
7. Validate với Product Service.

Definition of Done:

- User thêm sản phẩm vào giỏ.
- Cart tính đúng tổng tiền.
- Không thêm được sản phẩm hết hàng.
- Không thêm được sản phẩm không tồn tại.

---

## Giai đoạn 6 — Order Service

Thời lượng: 3 ngày.

Việc cần làm:

1. Tạo Order.
2. Tạo OrderItem.
3. Tạo checkout API.
4. Gọi Cart Service để lấy cart.
5. Gọi Product Service kiểm tra tồn kho.
6. Tạo order item snapshot.
7. Gọi Payment Service.
8. Gọi Shipping Service.
9. Clear cart sau khi order thành công.
10. API cập nhật trạng thái đơn.

Definition of Done:

- Checkout tạo đơn hàng thành công.
- Order có item snapshot.
- Có payment record.
- Có shipment record.
- User xem được order history.
- Staff cập nhật được trạng thái order.

---

## Giai đoạn 7 — Payment Service

Thời lượng: 1.5 - 2 ngày.

Việc cần làm:

1. Tạo Payment.
2. Tạo PaymentTransaction.
3. API tạo payment.
4. API giả lập success.
5. API giả lập failed.
6. API callback.
7. Order Service cập nhật payment_status.

Definition of Done:

- Payment được tạo khi checkout.
- Simulate success đổi trạng thái.
- Simulate failed đổi trạng thái.
- Order nhận được trạng thái thanh toán.

---

## Giai đoạn 8 — Shipping Service

Thời lượng: 1.5 - 2 ngày.

Việc cần làm:

1. Tạo Shipment.
2. API tính phí vận chuyển.
3. API tạo shipment.
4. API cập nhật trạng thái.
5. API tracking.

Definition of Done:

- Checkout tạo shipment.
- Shipment có tracking code.
- Staff cập nhật trạng thái giao hàng.
- User xem được trạng thái giao hàng.

---

## Giai đoạn 9 — Comment Service

Thời lượng: 1.5 - 2 ngày.

Việc cần làm:

1. Tạo Comment.
2. Tạo Review.
3. API tạo review.
4. API lấy review theo product.
5. API rating summary.
6. API reply comment.

Definition of Done:

- User review sản phẩm.
- Product detail hiển thị review.
- Rating trung bình tính đúng.
- AI Service có thể sync review.

---

## Giai đoạn 10 — AI Service bản 1: tracking + graph

Thời lượng: 2 - 3 ngày.

Việc cần làm:

1. Kết nối Neo4j.
2. Tạo endpoint `/api/ai/track`.
3. Ghi event VIEWED.
4. Ghi event ADD_TO_CART.
5. Ghi event PURCHASED.
6. Tạo node Product, User, Category.
7. Tạo relationship.
8. Tạo API recommend home theo graph.

Definition of Done:

- Khi user xem sản phẩm, Neo4j có quan hệ VIEWED.
- Khi user mua hàng, Neo4j có quan hệ PURCHASED.
- API `/api/ai/recommendations/home` trả sản phẩm gợi ý.

---

## Giai đoạn 11 — AI Service bản 2: embedding + pgvector

Thời lượng: 3 - 4 ngày.

Việc cần làm:

1. Đồng bộ product từ Product Service.
2. Build product document.
3. Generate embedding.
4. Save vào PostgreSQL + pgvector.
5. Tạo vector search API.
6. Tạo keyword search fallback.

Definition of Done:

- Có bảng `product_embedding`.
- Rebuild embedding thành công.
- Search bằng query text trả sản phẩm liên quan.

---

## Giai đoạn 12 — AI Service bản 3: RAG Chatbot

Thời lượng: 3 - 5 ngày.

Việc cần làm:

1. Tạo endpoint `/api/ai/chat`.
2. Nhận message từ user.
3. Intent detection đơn giản.
4. Hybrid Retrieval:
   - keyword search
   - vector search
   - graph search
5. Fusion/rerank kết quả.
6. Build context.
7. Generate answer bằng mock LLM hoặc LLM thật.
8. Trả danh sách sản phẩm gợi ý.

Definition of Done:

- User hỏi bằng tiếng Việt.
- AI trả lời được lý do gợi ý.
- AI trả về sản phẩm phù hợp.
- Có log nguồn retrieval.

---

## Giai đoạn 13 — API Gateway

Thời lượng: 2 ngày.

Việc cần làm:

1. Tạo route proxy theo path.
2. Cấu hình CORS.
3. Cấu hình JWT verify.
4. Forward header user.
5. Chuẩn hóa lỗi.
6. Log request.

Definition of Done:

- Frontend chỉ gọi gateway port 8000.
- Gateway route đúng sang service.
- Request có token được forward kèm user_id.
- Request lỗi trả format thống nhất.

---

## Giai đoạn 14 — Frontend khách hàng

Thời lượng: 4 - 5 ngày.

Việc cần làm:

1. Login/register.
2. Product listing.
3. Product detail.
4. Cart page.
5. Checkout page.
6. Order history.
7. Review UI.
8. Chatbot UI.
9. Recommended products UI.

Definition of Done:

- Người dùng thao tác được end-to-end.
- Chatbot hiển thị câu trả lời.
- Trang chủ có gợi ý sản phẩm.

---

## Giai đoạn 15 — Frontend admin/staff

Thời lượng: 3 - 4 ngày.

Việc cần làm:

1. Admin layout.
2. Product management.
3. Category management.
4. Order management.
5. Staff management.
6. Dashboard cơ bản.

Definition of Done:

- Admin quản lý được sản phẩm.
- Admin quản lý được đơn hàng.
- Admin cập nhật trạng thái đơn.
- Dashboard hiển thị số đơn, doanh thu, sản phẩm bán chạy.

---

## Giai đoạn 16 — Docker Compose hoàn chỉnh

Thời lượng: 2 ngày.

Việc cần làm:

1. Hoàn thiện Dockerfile từng service.
2. Gắn env.
3. Gắn volume database.
4. Viết script migrate.
5. Viết script seed.
6. Test start full system.
7. Viết README chạy project.

Definition of Done:

Chạy được:

```bash
docker compose up --build
```

Sau đó mở:

```text
Frontend: http://localhost:3000
Gateway:  http://localhost:8000
Neo4j:    http://localhost:7474
```

---

## 16. Testing plan

### 16.1. Unit test

Mỗi service test:

```text
model validation
serializer validation
service logic
JWT utils
```

### 16.2. API test

Test bằng Postman hoặc pytest:

```text
register/login
product CRUD
cart add/update/remove
checkout
payment simulate
shipping update
comment/review
ai chat
recommendation
```

### 16.3. Integration test

Các integration quan trọng:

```text
Cart -> Product
Order -> Cart
Order -> Product
Order -> Payment
Order -> Shipping
AI -> Product
AI -> Neo4j
AI -> pgvector
Gateway -> all services
```

### 16.4. End-to-end test checklist

```text
[ ] User đăng ký được
[ ] User đăng nhập được
[ ] User xem sản phẩm được
[ ] User thêm giỏ hàng được
[ ] User checkout được
[ ] Payment success được
[ ] Shipping được tạo
[ ] Order status cập nhật đúng
[ ] User review sản phẩm được
[ ] AI chatbot tư vấn được
[ ] Trang chủ có recommendation
[ ] Admin quản lý sản phẩm được
[ ] Admin quản lý order được
```

---

## 17. Thứ tự ưu tiên nếu thiếu thời gian

Nếu thời gian không đủ, làm theo thứ tự ưu tiên:

### Must-have

```text
User Service
Product Service
Cart Service
Order Service
Payment Service giả lập
Shipping Service giả lập
API Gateway
Frontend basic
Docker Compose
```

### Should-have

```text
Comment Service
Staff Service
Admin Dashboard
AI tracking
Neo4j recommendation
```

### Nice-to-have

```text
pgvector
RAG chatbot đầy đủ
Hybrid Retrieval Fusion
LLM thật
Redis cache
CI/CD
```

---

## 18. Rủi ro và cách xử lý

| Rủi ro | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Quá nhiều service | Khó hoàn thiện | Làm skeleton trước, core service trước |
| Docker Compose lỗi networking | Không gọi được service | Dùng service name làm host, không dùng localhost trong container |
| MySQL driver lỗi | Service không start | Dùng PyMySQL nếu mysqlclient lỗi |
| pgvector khó setup | AI vector không chạy | Dùng image `pgvector/pgvector:pg16` |
| Neo4j query khó | Recommendation lỗi | Làm query đơn giản VIEWED/PURCHASED trước |
| LLM tốn phí | Chatbot không chạy | Dùng mock LLM hoặc template response |
| JWT giữa service lệch secret | Auth lỗi | Dùng chung `JWT_SECRET` trong `.env` |
| Checkout distributed transaction phức tạp | Dữ liệu lệch | Dùng trạng thái PENDING/FAILED và compensating action đơn giản |

---

## 19. Chuẩn môi trường .env

```env
DJANGO_SECRET_KEY=dev-secret
JWT_SECRET=jwt-secret

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ecom
POSTGRES_USER=ecom
POSTGRES_PASSWORD=ecom

MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=ecom
MYSQL_USER=ecom
MYSQL_PASSWORD=ecom
MYSQL_ROOT_PASSWORD=root

NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

USER_SERVICE_URL=http://user_service:8001
STAFF_SERVICE_URL=http://staff_service:8002
PRODUCT_SERVICE_URL=http://product_service:8003
CART_SERVICE_URL=http://cart_service:8004
ORDER_SERVICE_URL=http://order_service:8005
PAYMENT_SERVICE_URL=http://payment_service:8006
SHIPPING_SERVICE_URL=http://shipping_service:8007
COMMENT_SERVICE_URL=http://comment_service:8008
AI_SERVICE_URL=http://ai_service:8009
```

---

## 20. Milestone tổng hợp

| Milestone | Kết quả |
|---|---|
| M1 | Docker Compose chạy database + skeleton service |
| M2 | User/Auth hoàn chỉnh |
| M3 | Product + Cart hoàn chỉnh |
| M4 | Order + Payment + Shipping hoàn chỉnh |
| M5 | Comment + Staff hoàn chỉnh |
| M6 | AI tracking + Neo4j recommendation |
| M7 | pgvector + RAG chatbot |
| M8 | API Gateway + Frontend |
| M9 | Test + seed data + demo video |
| M10 | Hoàn thiện báo cáo kỹ thuật |

---

## 21. Definition of Done toàn hệ thống

Hệ thống được coi là hoàn thành khi:

1. Chạy được bằng Docker Compose.
2. Có tối thiểu 8 service: gateway, user, staff, product, cart, order, payment, shipping, comment, ai.
3. Có PostgreSQL + pgvector.
4. Có MySQL.
5. Có Neo4j.
6. Có JWT custom.
7. Có frontend khách hàng.
8. Có frontend admin.
9. Có checkout end-to-end.
10. Có chatbot tư vấn sản phẩm.
11. Có recommendation dựa trên hành vi.
12. Có seed data để demo.
13. Có README hướng dẫn chạy.
14. Có Postman collection hoặc danh sách API.
15. Có sơ đồ kiến trúc và mô tả luồng xử lý.

---

## 22. Lệnh chạy dự kiến

```bash
git clone <repo-url>
cd ecom-final
cp .env.example .env
docker compose up --build
```

Migrate từng service:

```bash
docker compose exec user_service python manage.py migrate
docker compose exec staff_service python manage.py migrate
docker compose exec product_service python manage.py migrate
docker compose exec cart_service python manage.py migrate
docker compose exec order_service python manage.py migrate
docker compose exec payment_service python manage.py migrate
docker compose exec shipping_service python manage.py migrate
docker compose exec comment_service python manage.py migrate
docker compose exec ai_service python manage.py migrate
```

Seed data:

```bash
docker compose exec product_service python manage.py seed_products
docker compose exec user_service python manage.py seed_users
docker compose exec ai_service python manage.py sync_products
docker compose exec ai_service python manage.py rebuild_embeddings
```

---