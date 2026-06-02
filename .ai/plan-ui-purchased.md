# Plan - Modern Ecommerce UI and Purchased Graph Data

Last updated: 2026-06-02

## Goal

Improve the frontend so it looks and behaves more like a modern ecommerce site, while keeping the graph change conservative: use the currently supported `PURCHASED` event and create enough purchase data for a convincing Neo4j demo.

## Current Reality

The current AI behavior design already supports these event types:

```text
VIEWED
ADDED_TO_CART
PURCHASED
RATED
```

The current Neo4j code can already create relationships with these names. So this plan does not add many new event or relationship types. The gap is that demo data and UI flow do not create enough `PURCHASED` relationships yet.

## Scope

### In Scope

- Redesign `frontend/src/App.jsx` and `frontend/src/styles.css` into a cleaner ecommerce storefront.
- Keep the current React/Vite app structure unless splitting components becomes necessary.
- Wire successful checkout to create `PURCHASED` tracking events.
- Add a graph demo seed command that creates realistic `VIEWED`, `ADDED_TO_CART`, `PURCHASED`, and `RATED` data.
- Make recommendation logic give stronger weight to purchase behavior.
- Rebuild Docker and retest the core customer flow.

### Out of Scope

- Adding many new event types such as wishlist/search/recommendation-click.
- Adding derived graph relationships such as `CO_BOUGHT`, `CO_VIEWED`, or `SIMILAR_TO`.
- Reworking Neo4j schema beyond the existing user-product-category graph.
- Real payment provider integration.
- Full production admin/RBAC polish.

## Phase 1 - Frontend Redesign

### Visual Direction

Make the UI feel like a normal ecommerce site:

- Sticky top navigation with brand, search, cart, auth/profile.
- Product grid with image-first cards, clear price, category, stock, rating, and quick add.
- Product detail with large image, purchase panel, description, reviews, and related products.
- Cart page with quantity controls and order summary.
- Checkout page with shipping form and payment method selector.
- Order history with clear status badges.
- AI assistant as a shopping helper, not a raw technical demo panel.
- Admin/demo tools placed in a quieter operations area.

### Frontend Views To Improve

1. Storefront/product listing.
2. Product detail.
3. Cart.
4. Checkout.
5. Orders.
6. Recommendations.
7. Chatbot.
8. Admin/demo tools.

### Definition of Done

- `http://localhost:3000` looks like a recognizable ecommerce store.
- Main customer flow is usable from the UI: login/register, browse, detail, add cart, checkout, review, AI chat.
- Layout is responsive enough for desktop and mobile widths.
- Text and controls do not overlap or overflow.

## Phase 2 - PURCHASED Tracking

### Current Tracking

Frontend currently tracks:

```text
Product detail open -> VIEWED
Add to cart -> ADDED_TO_CART
Review submit -> RATED
```

### Required Change

After checkout succeeds, send one `PURCHASED` event per order item:

```json
{
  "product_id": 1,
  "event_type": "PURCHASED"
}
```

Use the existing `/api/ai/track` endpoint. No serializer/schema change should be needed for this basic purchase tracking.

### Preferred Implementation

For this pass, implement purchase tracking in the frontend after successful checkout because:

- The gateway/auth token is already available there.
- It avoids adding new service-to-service coupling from Order Service to AI Service.
- It is enough for a demo.

Later, this can move server-side if stronger correctness is needed.

### Definition of Done

- Completing checkout from the UI creates `PURCHASED` relationships in Neo4j.
- Existing `VIEWED`, `ADDED_TO_CART`, and `RATED` tracking still works.

## Phase 3 - Graph Demo Seed Data

### Add Management Command

Add an AI service command, for example:

```bash
docker compose exec -T ai_service python manage.py seed_graph_demo
```

The command should:

1. Sync products from Product Service if needed.
2. Create demo users in Neo4j.
3. Create `UserBehavior` rows using existing event types.
4. Upsert Neo4j relationships through the existing graph helper.

### Target Demo Data

Minimum useful seed:

```text
10 demo users
30 products
80 VIEWED events
30 ADDED_TO_CART events
30 PURCHASED events
20 RATED events
```

### Demo Personas

Create simple behavior clusters:

1. Programming learner.
2. AI/data reader.
3. Business reader.
4. Parent buying children books.
5. Language learner.

Each persona should purchase products from different categories so recommendations vary by user.

### Definition of Done

- Neo4j Browser shows enough `PURCHASED` edges to demo purchase behavior clearly.
- Seed can be rerun without creating messy duplicate relationships.
- Different seeded users get noticeably different recommendation results.

## Phase 4 - Recommendation Weighting

### Current Direction

The graph recommendation currently looks at behavior relationships and category overlap. Keep that approach, but make purchase behavior matter more.

### Scoring Direction

Use a simple priority:

```text
PURCHASED > ADDED_TO_CART > RATED > VIEWED
```

Exact scoring can stay simple:

```text
PURCHASED: 5
ADDED_TO_CART: 3
RATED: 2
VIEWED: 1
```

### Recommendation Behavior

- Products related to purchased categories should rank higher.
- Products already purchased should be excluded or deprioritized when possible.
- Fallback remains popular/category products when a user has no history.

### Definition of Done

- Recommendation output changes when a user has purchase history.
- `PURCHASED` relationships visibly influence recommendation ranking.

## Phase 5 - Verification

### Build/Runtime Checks

```bash
docker compose config --quiet
docker compose up -d --build
docker compose exec -T product_service python manage.py seed_products
docker compose exec -T ai_service python manage.py seed_graph_demo
```

### API Checks

```text
GET  /health on ports 8000-8009
POST /api/ai/sync-products
GET  /api/ai/recommendations/home
POST /api/ai/chat
```

### Manual UI Checks

1. Open `http://localhost:3000`.
2. Register/login.
3. Browse product list.
4. Open product detail.
5. Add product to cart.
6. Checkout.
7. Confirm `PURCHASED` exists in Neo4j.
8. Review product.
9. Ask chatbot for recommendations.

### Neo4j Demo Queries

```cypher
MATCH (u:User)-[r:PURCHASED]->(p:Product)
RETURN u, r, p
LIMIT 100;
```

```cypher
MATCH (u:User)-[r:VIEWED|ADDED_TO_CART|PURCHASED|RATED]->(p:Product)
RETURN u, r, p
LIMIT 100;
```

```cypher
MATCH (p:Product)-[r:IN_CATEGORY]->(c:Category)
RETURN p, r, c
LIMIT 100;
```

## Implementation Order

1. Redesign frontend layout and styling.
2. Wire checkout success to send `PURCHASED` tracking events.
3. Add `seed_graph_demo` command using existing event types.
4. Adjust recommendation weighting so `PURCHASED` matters more.
5. Rebuild Docker and run full flow.
6. Commit as a UI + purchased graph demo milestone.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| UI rewrite grows too large | Harder to maintain | Split components only if necessary |
| Checkout tracking fails silently | No purchase graph data | Log/catch tracking calls and verify in Neo4j |
| Seed command duplicates data | Messy graph | Use deterministic demo users and `MERGE` graph writes |
| Recommendation query becomes too complex | Bugs in demo | Keep fallback path simple |
| Product seed text has encoding issues | UI looks unpolished | Fix product seed text if it blocks demo quality |

## Done Criteria

- UI no longer feels like a rough technical demo.
- Checkout creates `PURCHASED` graph data.
- Neo4j Browser clearly shows `PURCHASED` relationships.
- Recommendations are influenced by purchase behavior.
- Full Docker flow still passes.
