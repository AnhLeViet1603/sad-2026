import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [token, setToken] = useState(localStorage.getItem("access_token") || "");
  const [view, setView] = useState("shop");
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState(null);
  const [orders, setOrders] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productReviews, setProductReviews] = useState([]);
  const [ratingSummary, setRatingSummary] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [message, setMessage] = useState("");

  const api = useMemo(() => {
    const client = axios.create({ baseURL: API_BASE });
    client.interceptors.request.use((config) => {
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
    return client;
  }, [token]);

  async function loadProducts() {
    const response = await api.get("/api/products");
    setProducts(response.data.data);
  }

  async function loadCart() {
    if (!token) return;
    const response = await api.get("/api/cart");
    setCart(response.data.data);
  }

  async function loadOrders() {
    if (!token) return;
    const response = await api.get("/api/orders");
    setOrders(response.data.data);
  }

  async function loadRecommendations() {
    const response = await api.get("/api/ai/recommendations/home");
    setRecommendations(response.data.data.products || []);
  }

  useEffect(() => {
    loadProducts().catch(showError);
    loadRecommendations().catch(() => {});
  }, []);

  useEffect(() => {
    loadCart().catch(() => {});
    loadOrders().catch(() => {});
  }, [token]);

  function showError(error) {
    const detail = error.response?.data?.error?.message || error.message;
    setMessage(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  async function handleAuth(mode, event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post(`/api/users/${mode}`, data);
    localStorage.setItem("access_token", response.data.data.access_token);
    localStorage.setItem("refresh_token", response.data.data.refresh_token);
    setToken(response.data.data.access_token);
    setMessage(mode === "login" ? "Đăng nhập thành công" : "Đăng ký thành công");
  }

  async function addToCart(product) {
    await api.post("/api/cart/items", { product_id: product.id, quantity: 1 });
    await api.post("/api/ai/track", { product_id: product.id, event_type: "ADDED_TO_CART" }).catch(() => {});
    await loadCart();
    setMessage("Đã thêm vào giỏ hàng");
  }

  async function openProductDetail(productId) {
    const [productResponse, relatedResponse, reviewsResponse, summaryResponse] = await Promise.all([
      api.get(`/api/products/${productId}`),
      api.get(`/api/products/${productId}/related`).catch(() => ({ data: { data: [] } })),
      api.get(`/api/comments/products/${productId}/reviews`).catch(() => ({ data: { data: [] } })),
      api.get(`/api/comments/products/${productId}/summary`).catch(() => ({ data: { data: null } })),
    ]);
    setSelectedProduct(productResponse.data.data);
    setRelatedProducts(relatedResponse.data.data || []);
    setProductReviews(reviewsResponse.data.data || []);
    setRatingSummary(summaryResponse.data.data);
    setView("product-detail");
    await api.post("/api/ai/track", { product_id: productId, event_type: "VIEWED" }).catch(() => {});
  }

  async function checkout(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    await api.post("/api/orders/checkout", {
      payment_method: data.payment_method,
      shipping_address: {
        receiver_name: data.receiver_name,
        phone: data.phone,
        province: data.province,
        district: data.district,
        ward: data.ward,
        detail: data.detail,
      },
    });
    await loadCart();
    await loadOrders();
    setMessage("Checkout thành công, payment/shipping đã được tạo giả lập");
  }

  async function review(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    await api.post("/api/comments/reviews", data);
    await api.post("/api/ai/track", { product_id: Number(data.product_id), event_type: "RATED" }).catch(() => {});
    setMessage("Đã gửi đánh giá");
  }

  async function reviewFromDetail(event) {
    event.preventDefault();
    if (!selectedProduct) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    await api.post("/api/comments/reviews", { ...data, product_id: selectedProduct.id });
    await api.post("/api/ai/track", { product_id: selectedProduct.id, event_type: "RATED" }).catch(() => {});
    await openProductDetail(selectedProduct.id);
    setMessage("Đã gửi đánh giá");
  }

  async function askBot(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post("/api/ai/chat", { message: data.message });
    setMessage(`${response.data.data.answer} (${response.data.data.products.length} sản phẩm)`);
    setRecommendations(response.data.data.products);
  }

  return (
    <main>
      <header className="topbar">
        <div>
          <h1>E-Commerce Demo</h1>
          <p>Microservices demo cho luồng khách hàng và quản trị.</p>
        </div>
        <nav>
          {["shop", "cart", "checkout", "orders", "ai", "admin"].map((item) => (
            <button className={view === item ? "active" : ""} key={item} onClick={() => setView(item)}>
              {item}
            </button>
          ))}
        </nav>
      </header>

      {message && <div className="status">{message}</div>}

      {!token && <AuthPanel onSubmit={handleAuth} showError={showError} />}

      {view === "shop" && <Shop products={products} onAdd={addToCart} onOpen={openProductDetail} />}
      {view === "product-detail" && selectedProduct && (
        <ProductDetail
          product={selectedProduct}
          reviews={productReviews}
          summary={ratingSummary}
          related={relatedProducts}
          onAdd={addToCart}
          onOpen={openProductDetail}
          onReview={reviewFromDetail}
          showError={showError}
        />
      )}
      {view === "cart" && <Cart cart={cart} reload={loadCart} api={api} showError={showError} />}
      {view === "checkout" && <Checkout cart={cart} onSubmit={checkout} showError={showError} />}
      {view === "orders" && <Orders orders={orders} api={api} reload={loadOrders} showError={showError} />}
      {view === "ai" && <AiPanel recommendations={recommendations} askBot={askBot} review={review} />}
      {view === "admin" && <AdminPanel api={api} products={products} reloadProducts={loadProducts} reloadOrders={loadOrders} showError={showError} />}
    </main>
  );
}

function AuthPanel({ onSubmit, showError }) {
  const [mode, setMode] = useState("login");
  return (
    <section className="band auth">
      <div className="segment">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
      </div>
      <form onSubmit={(event) => onSubmit(mode, event).catch(showError)}>
        <input name="email" type="email" placeholder="email" required />
        <input name="password" type="password" placeholder="password" required />
        {mode === "register" && <input name="full_name" placeholder="full name" required />}
        <button type="submit">{mode}</button>
      </form>
    </section>
  );
}

function Shop({ products, onAdd, onOpen }) {
  return (
    <section className="grid">
      {products.map((product) => (
        <article className="product" key={product.id}>
          <img src={product.images?.[0]?.image_url || "https://picsum.photos/seed/demo/480/640"} alt={product.name} />
          <h2>{product.name}</h2>
          <p>{product.description}</p>
          <div className="row">
            <strong>{Number(product.price).toLocaleString("vi-VN")}đ</strong>
            <button onClick={() => onOpen(product.id)}>Detail</button>
            <button onClick={() => onAdd(product)}>Add</button>
          </div>
        </article>
      ))}
    </section>
  );
}

function ProductDetail({ product, reviews, summary, related, onAdd, onOpen, onReview, showError }) {
  return (
    <section className="detail-layout">
      <div className="detail-media">
        <img src={product.images?.[0]?.image_url || "https://picsum.photos/seed/detail/800/600"} alt={product.name} />
      </div>
      <div className="detail-main">
        <p className="eyebrow">{product.brand || "Demo product"}</p>
        <h2>{product.name}</h2>
        <p>{product.description}</p>
        <div className="row">
          <strong>{Number(product.price).toLocaleString("vi-VN")}đ</strong>
          <span>{product.inventory?.available_quantity ?? 0} in stock</span>
          <button onClick={() => onAdd(product).catch(showError)}>Add to cart</button>
        </div>
        <div className="summary">
          <strong>{summary?.avg_rating || 0}/5</strong>
          <span>{summary?.review_count || 0} reviews</span>
        </div>
        <form className="form-grid" onSubmit={(event) => onReview(event).catch(showError)}>
          <input name="rating" type="number" min="1" max="5" placeholder="Rating" required />
          <input name="title" placeholder="Title" />
          <input name="content" placeholder="Review content" required />
          <button type="submit">Review</button>
        </form>
      </div>
      <div className="band detail-section">
        <h2>Reviews</h2>
        {reviews.map((review) => (
          <div className="review" key={review.id}>
            <strong>{review.rating}/5 {review.title}</strong>
            <p>{review.content}</p>
          </div>
        ))}
      </div>
      <div className="band detail-section">
        <h2>Related products</h2>
        <div className="recommendations">
          {related.map((item) => (
            <button key={item.id} onClick={() => onOpen(item.id).catch(showError)}>{item.name}</button>
          ))}
        </div>
      </div>
    </section>
  );
}

function Cart({ cart, reload, api, showError }) {
  async function remove(id) {
    await api.delete(`/api/cart/items/${id}`);
    await reload();
  }
  return (
    <section className="band">
      <h2>Cart</h2>
      {(cart?.items || []).map((item) => (
        <div className="line" key={item.id}>
          <span>{item.product_name}</span>
          <span>x{item.quantity}</span>
          <span>{Number(item.line_total).toLocaleString("vi-VN")}đ</span>
          <button onClick={() => remove(item.id).catch(showError)}>Remove</button>
        </div>
      ))}
      <strong>Total: {Number(cart?.total_amount || 0).toLocaleString("vi-VN")}đ</strong>
    </section>
  );
}

function Checkout({ cart, onSubmit, showError }) {
  return (
    <section className="band">
      <h2>Checkout</h2>
      <p>Subtotal: {Number(cart?.total_amount || 0).toLocaleString("vi-VN")}đ</p>
      <form className="form-grid" onSubmit={(event) => onSubmit(event).catch(showError)}>
        <input name="receiver_name" placeholder="Receiver name" required />
        <input name="phone" placeholder="Phone" required />
        <input name="province" placeholder="Province" required />
        <input name="district" placeholder="District" required />
        <input name="ward" placeholder="Ward" required />
        <input name="detail" placeholder="Address detail" required />
        <select name="payment_method" defaultValue="COD">
          <option value="COD">COD demo</option>
          <option value="BANK_TRANSFER">Bank transfer demo</option>
        </select>
        <button type="submit">Create order</button>
      </form>
    </section>
  );
}

function Orders({ orders, api, reload, showError }) {
  async function update(order, status) {
    await api.patch(`/api/orders/${order.id}/status`, { status });
    await reload();
  }
  return (
    <section className="band">
      <h2>Orders</h2>
      {orders.map((order) => (
        <div className="line" key={order.id}>
          <span>#{order.id}</span>
          <span>{order.status}</span>
          <span>{order.payment_status}</span>
          <span>{order.tracking_code || "no tracking"}</span>
          <button onClick={() => update(order, "CONFIRMED").catch(showError)}>Confirm</button>
        </div>
      ))}
    </section>
  );
}

function AiPanel({ recommendations, askBot, review }) {
  return (
    <section className="band">
      <h2>AI & Reviews</h2>
      <form onSubmit={askBot}>
        <input name="message" placeholder="Tôi muốn sách về AI hoặc lập trình" required />
        <button type="submit">Ask</button>
      </form>
      <form className="form-grid" onSubmit={review}>
        <input name="product_id" type="number" placeholder="Product ID" required />
        <input name="rating" type="number" min="1" max="5" placeholder="Rating" required />
        <input name="title" placeholder="Title" />
        <input name="content" placeholder="Review content" required />
        <button type="submit">Review</button>
      </form>
      <div className="recommendations">
        {recommendations.map((product) => (
          <span key={product.id}>{product.name}</span>
        ))}
      </div>
    </section>
  );
}

function AdminPanel({ api, products, reloadProducts, reloadOrders, showError }) {
  async function seedProducts() {
    await api.post("/api/ai/sync-products");
    await reloadProducts();
  }
  async function rebuildEmbeddings() {
    await api.post("/api/ai/rebuild-embeddings");
  }
  async function createCategory(event) {
    event.preventDefault();
    await api.post("/api/products/categories", Object.fromEntries(new FormData(event.currentTarget)));
    event.currentTarget.reset();
  }
  return (
    <section className="band">
      <h2>Admin</h2>
      <div className="row">
        <button onClick={() => reloadProducts().catch(showError)}>Reload products</button>
        <button onClick={() => reloadOrders().catch(showError)}>Reload orders</button>
        <button onClick={() => seedProducts().catch(showError)}>Sync AI products</button>
        <button onClick={() => rebuildEmbeddings().catch(showError)}>Rebuild embeddings</button>
      </div>
      <form className="form-grid" onSubmit={(event) => createCategory(event).catch(showError)}>
        <input name="name" placeholder="Category name" required />
        <input name="slug" placeholder="category-slug" required />
        <button type="submit">Add category</button>
      </form>
      <p>{products.length} products loaded.</p>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
