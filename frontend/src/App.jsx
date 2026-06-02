import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const viewLabels = {
  shop: "Shop",
  cart: "Cart",
  checkout: "Checkout",
  orders: "Orders",
  ai: "Assistant",
  admin: "Ops",
};

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
  const [searchTerm, setSearchTerm] = useState("");

  const api = useMemo(() => {
    const client = axios.create({ baseURL: API_BASE });
    client.interceptors.request.use((config) => {
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });
    return client;
  }, [token]);

  const cartCount = (cart?.items || []).reduce((sum, item) => sum + Number(item.quantity || 0), 0);
  const categories = useMemo(() => {
    const values = products.map((product) => product.category?.name || product.category).filter(Boolean);
    return [...new Set(values)].slice(0, 8);
  }, [products]);
  const filteredProducts = useMemo(() => {
    const keyword = searchTerm.trim().toLowerCase();
    if (!keyword) return products;
    return products.filter((product) => {
      const category = product.category?.name || product.category || "";
      return [product.name, product.description, product.brand, category].some((value) =>
        String(value || "").toLowerCase().includes(keyword)
      );
    });
  }, [products, searchTerm]);

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

  function requireAuth() {
    if (token) return true;
    setMessage("Please login before using cart, checkout, orders, or reviews.");
    return false;
  }

  async function handleAuth(mode, event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post(`/api/users/${mode}`, data);
    localStorage.setItem("access_token", response.data.data.access_token);
    localStorage.setItem("refresh_token", response.data.data.refresh_token);
    setToken(response.data.data.access_token);
    setMessage(mode === "login" ? "Logged in successfully." : "Account created successfully.");
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setToken("");
    setCart(null);
    setOrders([]);
    setMessage("Logged out.");
  }

  async function addToCart(product) {
    if (!requireAuth()) return;
    await api.post("/api/cart/items", { product_id: product.id, quantity: 1 });
    await api.post("/api/ai/track", { product_id: product.id, event_type: "ADDED_TO_CART" }).catch(() => {});
    await loadCart();
    setMessage(`${product.name} was added to cart.`);
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
    if (token) await api.post("/api/ai/track", { product_id: productId, event_type: "VIEWED" }).catch(() => {});
  }

  async function checkout(event) {
    event.preventDefault();
    if (!requireAuth()) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post("/api/orders/checkout", {
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
    const order = response.data.data;
    await Promise.all(
      (order.items || []).map((item) =>
        api.post("/api/ai/track", { product_id: item.product_id, event_type: "PURCHASED" }).catch(() => {})
      )
    );
    await loadCart();
    await loadOrders();
    await loadRecommendations().catch(() => {});
    setView("orders");
    setMessage(`Order #${order.id} created. Purchased events were sent to Neo4j.`);
  }

  async function reviewFromDetail(event) {
    event.preventDefault();
    if (!requireAuth() || !selectedProduct) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    await api.post("/api/comments/reviews", { ...data, product_id: selectedProduct.id });
    await api.post("/api/ai/track", { product_id: selectedProduct.id, event_type: "RATED" }).catch(() => {});
    await openProductDetail(selectedProduct.id);
    setMessage("Review submitted.");
  }

  async function askBot(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post("/api/ai/chat", { message: data.message });
    setMessage(response.data.data.answer);
    setRecommendations(response.data.data.products);
  }

  return (
    <main>
      <header className="topbar">
        <button className="brand" onClick={() => setView("shop")}>
          <span>MicroShop</span>
          <small>Book commerce demo</small>
        </button>
        <label className="searchbar">
          <span>Search</span>
          <input
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search books, categories, brands"
          />
        </label>
        <nav>
          {["shop", "cart", "checkout", "orders", "ai", "admin"].map((item) => (
            <button className={view === item ? "active" : ""} key={item} onClick={() => setView(item)}>
              {viewLabels[item]}
              {item === "cart" && cartCount > 0 ? <b>{cartCount}</b> : null}
            </button>
          ))}
        </nav>
        {token ? (
          <button className="ghost" onClick={logout}>Logout</button>
        ) : (
          <button className="ghost" onClick={() => setView("shop")}>Login</button>
        )}
      </header>

      {message && <div className="status">{message}</div>}

      {!token && <AuthPanel onSubmit={handleAuth} showError={showError} />}

      {view === "shop" && (
        <Shop
          products={filteredProducts}
          allProducts={products}
          categories={categories}
          recommendations={recommendations}
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
          onAdd={addToCart}
          onOpen={openProductDetail}
          showError={showError}
        />
      )}
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
      {view === "cart" && (
        <Cart cart={cart} setView={setView} reload={loadCart} api={api} showError={showError} />
      )}
      {view === "checkout" && <Checkout cart={cart} onSubmit={checkout} showError={showError} />}
      {view === "orders" && <Orders orders={orders} api={api} reload={loadOrders} showError={showError} />}
      {view === "ai" && <AiPanel recommendations={recommendations} askBot={askBot} onOpen={openProductDetail} />}
      {view === "admin" && (
        <AdminPanel
          api={api}
          products={products}
          reloadProducts={loadProducts}
          reloadOrders={loadOrders}
          reloadRecommendations={loadRecommendations}
          showError={showError}
        />
      )}
    </main>
  );
}

function AuthPanel({ onSubmit, showError }) {
  const [mode, setMode] = useState("login");
  return (
    <section className="auth-strip">
      <div>
        <strong>{mode === "login" ? "Welcome back" : "Create your demo account"}</strong>
        <span>Use any email and password for the local demo.</span>
      </div>
      <div className="segment">
        <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
        <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
      </div>
      <form className="auth-form" onSubmit={(event) => onSubmit(mode, event).catch(showError)}>
        <input name="email" type="email" placeholder="email@example.com" required />
        <input name="password" type="password" placeholder="Password" required />
        {mode === "register" && <input name="full_name" placeholder="Full name" required />}
        <button type="submit">{mode === "login" ? "Login" : "Create account"}</button>
      </form>
    </section>
  );
}

function Shop({ products, allProducts, categories, recommendations, searchTerm, setSearchTerm, onAdd, onOpen, showError }) {
  const featured = recommendations.length ? recommendations : allProducts.slice(0, 6);
  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">Microservices bookstore</p>
          <h1>Find the next book your graph already knows you want.</h1>
          <p>
            Browse seeded products, add them to cart, checkout, and watch Neo4j learn from viewed, carted, rated, and
            purchased behavior.
          </p>
          <div className="hero-actions">
            <button onClick={() => document.querySelector(".catalog-grid")?.scrollIntoView({ behavior: "smooth" })}>
              Shop catalog
            </button>
            <button className="secondary" onClick={() => setSearchTerm("AI")}>Explore AI books</button>
          </div>
        </div>
        <div className="hero-panel">
          <span>Live catalog</span>
          <strong>{allProducts.length}</strong>
          <small>products synced through the gateway</small>
        </div>
      </section>

      <section className="category-row">
        <button className={!searchTerm ? "active" : ""} onClick={() => setSearchTerm("")}>All</button>
        {categories.map((category) => (
          <button key={category} onClick={() => setSearchTerm(category)}>{category}</button>
        ))}
      </section>

      <ProductRail title="Recommended for you" products={featured} onAdd={onAdd} onOpen={onOpen} showError={showError} />

      <section className="section-head">
        <div>
          <p className="eyebrow">Catalog</p>
          <h2>{searchTerm ? `Results for "${searchTerm}"` : "All products"}</h2>
        </div>
        <span>{products.length} items</span>
      </section>
      <section className="catalog-grid">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} onAdd={onAdd} onOpen={onOpen} showError={showError} />
        ))}
      </section>
    </>
  );
}

function ProductRail({ title, products, onAdd, onOpen, showError }) {
  if (!products.length) return null;
  return (
    <section className="rail">
      <div className="section-head compact">
        <h2>{title}</h2>
        <span>{products.length} picks</span>
      </div>
      <div className="rail-scroll">
        {products.slice(0, 8).map((product) => (
          <ProductCard key={product.id} product={product} onAdd={onAdd} onOpen={onOpen} showError={showError} compact />
        ))}
      </div>
    </section>
  );
}

function ProductCard({ product, onAdd, onOpen, showError, compact = false }) {
  const category = product.category?.name || product.category || "Book";
  return (
    <article className={compact ? "product-card compact-card" : "product-card"}>
      <button className="image-button" onClick={() => onOpen(product.id).catch(showError)}>
        <img src={product.images?.[0]?.image_url || `https://picsum.photos/seed/book-${product.id}/520/640`} alt={product.name} />
      </button>
      <div className="product-body">
        <div className="product-meta">
          <span>{category}</span>
          <span>{product.inventory?.available_quantity ?? product.stock ?? 0} left</span>
        </div>
        <h3>{product.name}</h3>
        {!compact && <p>{product.description}</p>}
        <div className="product-actions">
          <strong>{formatPrice(product.price)}</strong>
          <button onClick={() => onAdd(product).catch(showError)}>Add</button>
        </div>
      </div>
    </article>
  );
}

function ProductDetail({ product, reviews, summary, related, onAdd, onOpen, onReview, showError }) {
  const category = product.category?.name || product.category || "Book";
  return (
    <>
      <section className="product-detail">
        <div className="detail-gallery">
          <img src={product.images?.[0]?.image_url || `https://picsum.photos/seed/detail-${product.id}/900/720`} alt={product.name} />
        </div>
        <div className="detail-copy">
          <p className="eyebrow">{category}</p>
          <h1>{product.name}</h1>
          <p>{product.description}</p>
          <div className="detail-stats">
            <span>{summary?.avg_rating || 0}/5 rating</span>
            <span>{summary?.review_count || 0} reviews</span>
            <span>{product.inventory?.available_quantity ?? 0} in stock</span>
          </div>
        </div>
        <aside className="purchase-box">
          <span>Price</span>
          <strong>{formatPrice(product.price)}</strong>
          <button onClick={() => onAdd(product).catch(showError)}>Add to cart</button>
          <small>Checkout will create PURCHASED graph relationships for this product.</small>
        </aside>
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="section-head compact">
            <h2>Customer reviews</h2>
            <span>{reviews.length} shown</span>
          </div>
          {reviews.length ? (
            reviews.map((review) => (
              <div className="review" key={review.id}>
                <strong>{review.rating}/5 {review.title}</strong>
                <p>{review.content}</p>
              </div>
            ))
          ) : (
            <p>No reviews yet.</p>
          )}
        </div>
        <form className="panel review-form" onSubmit={(event) => onReview(event).catch(showError)}>
          <h2>Write a review</h2>
          <input name="rating" type="number" min="1" max="5" placeholder="Rating 1-5" required />
          <input name="title" placeholder="Review title" />
          <textarea name="content" placeholder="What should other shoppers know?" required />
          <button type="submit">Submit review</button>
        </form>
      </section>

      <ProductRail title="Related products" products={related} onAdd={onAdd} onOpen={onOpen} showError={showError} />
    </>
  );
}

function Cart({ cart, setView, reload, api, showError }) {
  async function remove(id) {
    await api.delete(`/api/cart/items/${id}`);
    await reload();
  }

  const items = cart?.items || [];
  return (
    <section className="checkout-layout">
      <div className="panel">
        <div className="section-head compact">
          <h2>Your cart</h2>
          <span>{items.length} lines</span>
        </div>
        {items.length ? (
          items.map((item) => (
            <div className="cart-line" key={item.id}>
              <img src={item.image_url || `https://picsum.photos/seed/cart-${item.product_id}/160/160`} alt={item.product_name} />
              <div>
                <strong>{item.product_name}</strong>
                <span>Quantity {item.quantity}</span>
              </div>
              <strong>{formatPrice(item.line_total)}</strong>
              <button className="ghost danger" onClick={() => remove(item.id).catch(showError)}>Remove</button>
            </div>
          ))
        ) : (
          <p>Your cart is empty.</p>
        )}
      </div>
      <OrderSummary cart={cart} actionLabel="Checkout" onAction={() => setView("checkout")} disabled={!items.length} />
    </section>
  );
}

function Checkout({ cart, onSubmit, showError }) {
  return (
    <section className="checkout-layout">
      <form className="panel checkout-form" onSubmit={(event) => onSubmit(event).catch(showError)}>
        <div>
          <p className="eyebrow">Shipping</p>
          <h2>Delivery details</h2>
        </div>
        <input name="receiver_name" placeholder="Receiver name" required />
        <input name="phone" placeholder="Phone" required />
        <div className="form-two">
          <input name="province" placeholder="Province" required />
          <input name="district" placeholder="District" required />
        </div>
        <input name="ward" placeholder="Ward" required />
        <textarea name="detail" placeholder="Address detail" required />
        <select name="payment_method" defaultValue="COD">
          <option value="COD">Cash on delivery demo</option>
          <option value="BANK_TRANSFER">Bank transfer demo</option>
        </select>
        <button type="submit">Place order</button>
      </form>
      <OrderSummary cart={cart} actionLabel="Place order" muted />
    </section>
  );
}

function OrderSummary({ cart, actionLabel, onAction, disabled, muted = false }) {
  const subtotal = Number(cart?.total_amount || 0);
  const shipping = subtotal > 0 ? 30000 : 0;
  return (
    <aside className="summary-box">
      <h2>Order summary</h2>
      <div><span>Subtotal</span><strong>{formatPrice(subtotal)}</strong></div>
      <div><span>Shipping</span><strong>{formatPrice(shipping)}</strong></div>
      <div className="total"><span>Total</span><strong>{formatPrice(subtotal + shipping)}</strong></div>
      {!muted && <button disabled={disabled} onClick={onAction}>{actionLabel}</button>}
    </aside>
  );
}

function Orders({ orders, api, reload, showError }) {
  async function update(order, status) {
    await api.patch(`/api/orders/${order.id}/status`, { status });
    await reload();
  }
  return (
    <section className="panel wide-panel">
      <div className="section-head compact">
        <h2>Orders</h2>
        <span>{orders.length} total</span>
      </div>
      {orders.length ? (
        orders.map((order) => (
          <article className="order-row" key={order.id}>
            <div>
              <strong>Order #{order.id}</strong>
              <span>{order.items?.length || 0} items · {formatPrice(order.total_amount)}</span>
            </div>
            <StatusBadge label={order.status} />
            <StatusBadge label={order.payment_status} />
            <span>{order.tracking_code || "No tracking yet"}</span>
            <button onClick={() => update(order, "CONFIRMED").catch(showError)}>Confirm</button>
          </article>
        ))
      ) : (
        <p>No orders yet.</p>
      )}
    </section>
  );
}

function AiPanel({ recommendations, askBot, onOpen }) {
  return (
    <section className="assistant-layout">
      <form className="assistant-box" onSubmit={askBot}>
        <p className="eyebrow">Shopping assistant</p>
        <h1>Ask for a recommendation</h1>
        <p>Responses use product documents, vector/keyword retrieval, and graph behavior when available.</p>
        <textarea name="message" placeholder="Recommend books for learning AI and programming" required />
        <button type="submit">Ask assistant</button>
      </form>
      <div className="panel">
        <div className="section-head compact">
          <h2>Recommendation results</h2>
          <span>{recommendations.length} products</span>
        </div>
        <div className="mini-list">
          {recommendations.map((product) => (
            <button key={product.id} onClick={() => onOpen(product.id)}>
              <strong>{product.name}</strong>
              <span>{formatPrice(product.price)} · {(product.sources || []).join(", ") || "popular"}</span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function AdminPanel({ api, products, reloadProducts, reloadOrders, reloadRecommendations, showError }) {
  async function syncProducts() {
    await api.post("/api/ai/sync-products");
    await reloadProducts();
    await reloadRecommendations();
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
    <section className="ops-layout">
      <div className="panel">
        <p className="eyebrow">Operations</p>
        <h2>Demo controls</h2>
        <div className="ops-actions">
          <button onClick={() => reloadProducts().catch(showError)}>Reload products</button>
          <button onClick={() => reloadOrders().catch(showError)}>Reload orders</button>
          <button onClick={() => syncProducts().catch(showError)}>Sync AI products</button>
          <button onClick={() => rebuildEmbeddings().catch(showError)}>Rebuild embeddings</button>
        </div>
        <p>{products.length} products loaded. Run `seed_graph_demo` in the AI container for purchase graph data.</p>
      </div>
      <form className="panel checkout-form" onSubmit={(event) => createCategory(event).catch(showError)}>
        <h2>Add category</h2>
        <input name="name" placeholder="Category name" required />
        <input name="slug" placeholder="category-slug" required />
        <button type="submit">Create category</button>
      </form>
    </section>
  );
}

function StatusBadge({ label }) {
  return <span className={`badge ${String(label || "").toLowerCase()}`}>{label || "UNKNOWN"}</span>;
}

function formatPrice(value) {
  return `${Number(value || 0).toLocaleString("vi-VN")} VND`;
}

createRoot(document.getElementById("root")).render(<App />);
