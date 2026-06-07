import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Link, NavLink, Route, Routes, useNavigate, useParams } from "react-router-dom";
import axios from "axios";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  return (
    <BrowserRouter>
      <StoreApp />
    </BrowserRouter>
  );
}

function StoreApp() {
  const [token, setToken] = useState(localStorage.getItem("access_token") || "");
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState(null);
  const [orders, setOrders] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
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
    const byId = new Map();
    products.forEach((product) => {
      const category = normalizeCategory(product.category);
      if (category) byId.set(category.id || category.slug || category.name, category);
    });
    return [...byId.values()].slice(0, 10);
  }, [products]);
  const filteredProducts = useMemo(() => filterProducts(products, searchTerm), [products, searchTerm]);

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

  const common = {
    api,
    token,
    products,
    cart,
    orders,
    recommendations,
    searchTerm,
    categories,
    filteredProducts,
    setToken,
    setMessage,
    setSearchTerm,
    showError,
    requireAuth,
    addToCart,
    loadProducts,
    loadCart,
    loadOrders,
    loadRecommendations,
  };

  return (
    <main>
      <Header
        token={token}
        cartCount={cartCount}
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        logout={logout}
      />
      {message && <div className="status">{message}</div>}
      <Routes>
        <Route path="/" element={<HomePage {...common} />} />
        <Route path="/products" element={<ProductsPage {...common} />} />
        <Route path="/products/:productId" element={<ProductDetailPage {...common} />} />
        <Route path="/cart" element={<CartPage {...common} />} />
        <Route path="/checkout" element={<CheckoutPage {...common} />} />
        <Route path="/orders" element={<OrdersPage {...common} />} />
        <Route path="/login" element={<AuthPage handleAuth={handleAuth} showError={showError} />} />
        <Route path="/assistant" element={<AssistantPage {...common} />} />
        <Route path="/admin" element={<AdminPage {...common} />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </main>
  );
}

function Header({ token, cartCount, searchTerm, setSearchTerm, logout }) {
  return (
    <header className="topbar">
      <Link className="brand" to="/">
        <span>MicroShop</span>
        <small>Composable ecommerce demo</small>
      </Link>
      <label className="searchbar">
        <span>Search</span>
        <input
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          placeholder="Search products, categories, brands"
        />
      </label>
      <nav>
        <NavLink to="/products">Products</NavLink>
        <NavLink to="/cart">Cart{cartCount > 0 ? <b>{cartCount}</b> : null}</NavLink>
        <NavLink to="/orders">Orders</NavLink>
        <NavLink to="/assistant">Assistant</NavLink>
        <NavLink to="/admin">Admin</NavLink>
      </nav>
      {token ? (
        <button className="ghost" onClick={logout}>Logout</button>
      ) : (
        <Link className="button ghost" to="/login">Login</Link>
      )}
    </header>
  );
}

function HomePage({ products, recommendations, categories, setSearchTerm, addToCart, showError }) {
  const featured = recommendations.length ? recommendations : products.slice(0, 6);
  return (
    <>
      <section className="hero">
        <div>
          <p className="eyebrow">Microservices commerce</p>
          <h1>Shop a live product catalog powered by microservices.</h1>
          <p>
            Browse products, add items to cart, checkout, and let the recommendation graph learn from real customer
            behavior.
          </p>
          <div className="hero-actions">
            <Link className="button" to="/products">Shop products</Link>
            <button className="secondary" onClick={() => setSearchTerm("smart")}>Explore smart picks</button>
          </div>
        </div>
        <div className="hero-panel">
          <span>Live catalog</span>
          <strong>{products.length}</strong>
          <small>products available through the API gateway</small>
        </div>
      </section>
      <CategoryRow categories={categories} setSearchTerm={setSearchTerm} />
      <ProductRail title="Recommended for you" products={featured} onAdd={addToCart} showError={showError} />
    </>
  );
}

function ProductsPage({ filteredProducts, products, categories, searchTerm, setSearchTerm, addToCart, showError }) {
  return (
    <>
      <CategoryRow categories={categories} setSearchTerm={setSearchTerm} activeTerm={searchTerm} />
      <section className="section-head">
        <div>
          <p className="eyebrow">Catalog</p>
          <h2>{searchTerm ? `Results for "${searchTerm}"` : "All products"}</h2>
        </div>
        <span>{filteredProducts.length} of {products.length} items</span>
      </section>
      {filteredProducts.length ? (
        <section className="catalog-grid">
          {filteredProducts.map((product) => (
            <ProductCard key={product.id} product={product} onAdd={addToCart} showError={showError} />
          ))}
        </section>
      ) : (
        <EmptyState title="No products found" body="Try clearing the category or search keyword." />
      )}
    </>
  );
}

function ProductDetailPage({ api, token, addToCart, showError, requireAuth, setMessage }) {
  const { productId } = useParams();
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [summary, setSummary] = useState(null);
  const [related, setRelated] = useState([]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const [productResponse, relatedResponse, reviewsResponse, summaryResponse] = await Promise.all([
        api.get(`/api/products/${productId}`),
        api.get(`/api/products/${productId}/related`).catch(() => ({ data: { data: [] } })),
        api.get(`/api/comments/products/${productId}/reviews`).catch(() => ({ data: { data: [] } })),
        api.get(`/api/comments/products/${productId}/summary`).catch(() => ({ data: { data: null } })),
      ]);
      if (cancelled) return;
      setProduct(productResponse.data.data);
      setRelated(relatedResponse.data.data || []);
      setReviews(reviewsResponse.data.data || []);
      setSummary(summaryResponse.data.data);
      if (token) await api.post("/api/ai/track", { product_id: Number(productId), event_type: "VIEWED" }).catch(() => {});
    }
    load().catch(showError);
    return () => {
      cancelled = true;
    };
  }, [api, productId, token]);

  async function review(event) {
    event.preventDefault();
    if (!requireAuth() || !product) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    await api.post("/api/comments/reviews", { ...data, product_id: product.id });
    await api.post("/api/ai/track", { product_id: product.id, event_type: "RATED" }).catch(() => {});
    setMessage("Review submitted.");
    event.currentTarget.reset();
  }

  if (!product) return <EmptyState title="Loading product" body="Fetching product details from Product Service." />;

  return (
    <>
      <section className="product-detail">
        <div className="detail-gallery">
          <img src={productImage(product, "detail")} alt={product.name} />
        </div>
        <div className="detail-copy">
          <p className="eyebrow">{categoryName(product.category)}</p>
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
          <button onClick={() => addToCart(product).catch(showError)}>Add to cart</button>
          <small>Checkout creates PURCHASED relationships in the recommendation graph.</small>
        </aside>
      </section>
      <section className="content-grid">
        <div className="panel">
          <div className="section-head compact">
            <h2>Customer reviews</h2>
            <span>{reviews.length} shown</span>
          </div>
          {reviews.length ? reviews.map((item) => (
            <div className="review" key={item.id}>
              <strong>{item.rating}/5 {item.title}</strong>
              <p>{item.content}</p>
            </div>
          )) : <p>No reviews yet.</p>}
        </div>
        <form className="panel review-form" onSubmit={(event) => review(event).catch(showError)}>
          <h2>Write a review</h2>
          <input name="rating" type="number" min="1" max="5" placeholder="Rating 1-5" required />
          <input name="title" placeholder="Review title" />
          <textarea name="content" placeholder="What should other shoppers know?" required />
          <button type="submit">Submit review</button>
        </form>
      </section>
      <ProductRail title="Related products" products={related} onAdd={addToCart} showError={showError} />
    </>
  );
}

function CartPage({ cart, loadCart, api, showError }) {
  async function remove(id) {
    await api.delete(`/api/cart/items/${id}`);
    await loadCart();
  }
  const items = cart?.items || [];
  return (
    <section className="checkout-layout">
      <div className="panel">
        <div className="section-head compact">
          <h2>Your cart</h2>
          <span>{items.length} lines</span>
        </div>
        {items.length ? items.map((item) => (
          <div className="cart-line" key={item.id}>
            <img src={item.image_url || `https://picsum.photos/seed/cart-${item.product_id}/160/160`} alt={item.product_name} />
            <div>
              <strong>{item.product_name}</strong>
              <span>Quantity {item.quantity}</span>
            </div>
            <strong>{formatPrice(item.line_total)}</strong>
            <button className="ghost danger" onClick={() => remove(item.id).catch(showError)}>Remove</button>
          </div>
        )) : <p>Your cart is empty.</p>}
      </div>
      <OrderSummary cart={cart} action={<Link className="button" to="/checkout">Checkout</Link>} />
    </section>
  );
}

function CheckoutPage({ cart, api, requireAuth, loadCart, loadOrders, loadRecommendations, showError, setMessage }) {
  const navigate = useNavigate();
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
    setMessage(`Order #${order.id} created.`);
    navigate("/orders");
  }
  return (
    <section className="checkout-layout">
      <form className="panel checkout-form" onSubmit={(event) => checkout(event).catch(showError)}>
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
      <OrderSummary cart={cart} />
    </section>
  );
}

function OrdersPage({ orders, api, loadOrders, showError }) {
  async function update(order, status) {
    await api.patch(`/api/orders/${order.id}/status`, { status });
    await loadOrders();
  }
  return (
    <section className="panel wide-panel">
      <div className="section-head compact">
        <h2>Orders</h2>
        <span>{orders.length} total</span>
      </div>
      {orders.length ? orders.map((order) => (
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
      )) : <p>No orders yet.</p>}
    </section>
  );
}

function AuthPage({ handleAuth, showError }) {
  const [mode, setMode] = useState("login");
  const navigate = useNavigate();
  async function submit(event) {
    await handleAuth(mode, event);
    navigate("/products");
  }
  return (
    <section className="auth-page">
      <div className="panel auth-panel">
        <p className="eyebrow">Account</p>
        <h1>{mode === "login" ? "Welcome back" : "Create your demo account"}</h1>
        <p>Use any email and password for the local ecommerce demo.</p>
        <div className="segment">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Register</button>
        </div>
        <form className="checkout-form" onSubmit={(event) => submit(event).catch(showError)}>
          <input name="email" type="email" placeholder="email@example.com" required />
          <input name="password" type="password" placeholder="Password" required />
          {mode === "register" && <input name="full_name" placeholder="Full name" required />}
          <button type="submit">{mode === "login" ? "Login" : "Create account"}</button>
        </form>
      </div>
    </section>
  );
}

function AssistantPage({ api, recommendations, showError }) {
  const [answer, setAnswer] = useState("");
  const [items, setItems] = useState(recommendations);
  async function ask(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    const response = await api.post("/api/ai/chat", { message: data.message });
    setAnswer(response.data.data.answer);
    setItems(response.data.data.products);
  }
  return (
    <section className="assistant-layout">
      <form className="assistant-box" onSubmit={(event) => ask(event).catch(showError)}>
        <p className="eyebrow">Shopping assistant</p>
        <h1>Ask for a recommendation</h1>
        <p>Responses use product documents, vector/keyword retrieval, and graph behavior when available.</p>
        <textarea name="message" placeholder="Recommend products for my needs" required />
        <button type="submit">Ask assistant</button>
      </form>
      <div className="panel">
        <h2>Recommendation results</h2>
        {answer && <p>{answer}</p>}
        <div className="mini-list">
          {items.map((product) => (
            <Link key={product.id} to={`/products/${product.id}`}>
              <strong>{product.name}</strong>
              <span>{formatPrice(product.price)} · {(product.sources || []).join(", ") || "popular"}</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

function AdminPage({ api, products, loadProducts, loadOrders, loadRecommendations, showError }) {
  async function syncProducts() {
    await api.post("/api/ai/sync-products");
    await loadProducts();
    await loadRecommendations();
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
        <p className="eyebrow">Admin tools</p>
        <h2>Demo controls</h2>
        <div className="ops-actions">
          <button onClick={() => loadProducts().catch(showError)}>Reload products</button>
          <button onClick={() => loadOrders().catch(showError)}>Reload orders</button>
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

function CategoryRow({ categories, setSearchTerm, activeTerm = "" }) {
  return (
    <section className="category-row">
      <button className={!activeTerm ? "active" : ""} onClick={() => setSearchTerm("")}>All</button>
      {categories.map((category) => (
        <button
          className={activeTerm === category.name ? "active" : ""}
          key={category.id || category.slug || category.name}
          onClick={() => setSearchTerm(category.name)}
        >
          {category.name}
        </button>
      ))}
    </section>
  );
}

function ProductRail({ title, products, onAdd, showError }) {
  if (!products.length) return null;
  return (
    <section className="rail">
      <div className="section-head compact">
        <h2>{title}</h2>
        <span>{products.length} picks</span>
      </div>
      <div className="rail-scroll">
        {products.slice(0, 8).map((product) => (
          <ProductCard key={product.id} product={product} onAdd={onAdd} showError={showError} compact />
        ))}
      </div>
    </section>
  );
}

function ProductCard({ product, onAdd, showError, compact = false }) {
  return (
    <article className={compact ? "product-card compact-card" : "product-card"}>
      <Link className="image-button" to={`/products/${product.id}`}>
        <img src={productImage(product)} alt={product.name} />
      </Link>
      <div className="product-body">
        <div className="product-meta">
          <span>{categoryName(product.category)}</span>
          <span>{product.inventory?.available_quantity ?? product.stock ?? 0} left</span>
        </div>
        <h3><Link to={`/products/${product.id}`}>{product.name}</Link></h3>
        {!compact && <p>{product.description}</p>}
        <div className="product-actions">
          <strong>{formatPrice(product.price)}</strong>
          <button onClick={() => onAdd(product).catch(showError)}>Add</button>
        </div>
      </div>
    </article>
  );
}

function OrderSummary({ cart, action = null }) {
  const subtotal = Number(cart?.total_amount || 0);
  const shipping = subtotal > 0 ? 30000 : 0;
  return (
    <aside className="summary-box">
      <h2>Order summary</h2>
      <div><span>Subtotal</span><strong>{formatPrice(subtotal)}</strong></div>
      <div><span>Shipping</span><strong>{formatPrice(shipping)}</strong></div>
      <div className="total"><span>Total</span><strong>{formatPrice(subtotal + shipping)}</strong></div>
      {action}
    </aside>
  );
}

function StatusBadge({ label }) {
  return <span className={`badge ${String(label || "").toLowerCase()}`}>{label || "UNKNOWN"}</span>;
}

function EmptyState({ title, body }) {
  return (
    <section className="empty-state">
      <h2>{title}</h2>
      <p>{body}</p>
    </section>
  );
}

function NotFoundPage() {
  return <EmptyState title="Page not found" body="Use the navigation to return to the catalog." />;
}

function normalizeCategory(category) {
  if (!category) return null;
  if (typeof category === "object") return category;
  return { id: String(category), name: String(category), slug: String(category) };
}

function categoryName(category) {
  return normalizeCategory(category)?.name || "General";
}

function filterProducts(products, searchTerm) {
  const keyword = String(searchTerm || "").trim().toLowerCase();
  if (!keyword) return products;
  return products.filter((product) => {
    const category = categoryName(product.category);
    return [product.name, product.description, product.brand, category].some((value) =>
      String(value || "").toLowerCase().includes(keyword)
    );
  });
}

function productImage(product, seed = "product") {
  return product.images?.[0]?.image_url || `https://picsum.photos/seed/${seed}-${product.id}/520/640`;
}

function formatPrice(value) {
  return `${Number(value || 0).toLocaleString("vi-VN")} VND`;
}

createRoot(document.getElementById("root")).render(<App />);
