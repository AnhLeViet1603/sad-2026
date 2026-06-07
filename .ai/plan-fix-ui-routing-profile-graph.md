# Plan - Fix Ecommerce Routing, Profile Checkout, Chat Assistant, and Graph Tracking

Last updated: 2026-06-07

## Goal

Fix the current frontend architecture and demo behavior so it matches a normal ecommerce site:

- Every major screen has its own URL.
- The site is not presented as a bookstore.
- Categories show readable names and do not crash the UI.
- Checkout uses saved user address/profile data.
- Assistant appears as a floating ecommerce chat widget.
- Internal demo ops controls are removed from the customer UI.
- Neo4j interaction tracking is kept as-is for now.

## Current Diagnosis

1. Routing is state-based with `view`/`setView`, so URLs do not change.
2. UI copy and fallback images/text currently frame the shop as a bookstore.
3. Product API returns `category` as an ID because `ProductSerializer` uses the default FK representation.
4. Category chips are built from `product.category`; that produces `6`, `5`, `4`, etc.
5. Clicking a numeric category passes a number into `searchTerm`; filtering then calls `.trim()` and can crash the UI.
6. Checkout form is manually typed every time; it does not read `GET /api/users/addresses`.
7. Assistant is implemented as a full tab, not a floating chat widget.
8. Ops is just a demo/admin control area for sync/reload/rebuild; it should not appear in customer navigation.
9. Neo4j tracking appears to work; missing interactions in Browser are likely caused by small query limits or querying the wrong user slice.

## Phase 1 - Real Frontend Routing

Use `react-router-dom` or a small router based on browser history. Prefer `react-router-dom` if dependency install is acceptable.

Routes:

```text
/                  Home/storefront
/products          Product listing
/products/:id      Product detail
/cart              Cart
/checkout          Checkout
/orders            Order history
/account           Profile and saved addresses
/login             Login/register
/admin             Internal admin/demo tools, not in customer nav
```

Navigation should use links, not `setView`.

Definition of done:

- Browser URL changes per page.
- Refreshing a URL keeps the same page.
- Product detail has a real route like `/products/30`.

## Phase 2 - General Ecommerce UI

Remove bookstore-specific copy:

- Replace `Book commerce demo`, `bookstore`, `books`, `AI books` with general ecommerce language.
- Product cards should support any product: image, name, category, brand, price, stock.
- Hero should communicate a general ecommerce store, not a book shop.

Definition of done:

- UI no longer reads like a bookstore.
- Product/category/brand labels work for generic products.

## Phase 3 - Category Data Fix

Backend options:

1. Best fix: expose nested category data in `ProductSerializer`.
2. Also keep write support with `category_id` for admin create/update if needed.

Target product response:

```json
{
  "id": 1,
  "name": "Product",
  "category": {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics"
  }
}
```

Frontend:

- Use category object safely.
- Category chips should filter by `slug` or `id`, not by search text.
- Add an empty state instead of a blank page.

Definition of done:

- Category chips show names, not numbers.
- Clicking category never crashes.
- Empty category/search result shows a friendly empty state.

## Phase 4 - Profile And Delivery Details

Use User Service address APIs:

```text
GET  /api/users/me
GET  /api/users/addresses
POST /api/users/addresses
PATCH /api/users/addresses/:id
DELETE /api/users/addresses/:id
```

Frontend changes:

- Add `/account` page.
- Let user create/edit saved delivery addresses.
- Checkout loads default address.
- Checkout should allow selecting a saved address.
- If no address exists, checkout asks user to create one and can save it.

Definition of done:

- User does not retype delivery details every checkout.
- Checkout payload is built from selected saved address.

## Phase 5 - Floating Assistant Widget

Remove Assistant from top-level tab navigation.

Add a floating chat launcher:

- Bottom-right button.
- Opens a compact chat panel.
- Shows message history.
- Sends message to `/api/ai/chat`.
- Shows recommended products inside the chat.
- Product links navigate to `/products/:id`.

Definition of done:

- Chat feels like an ecommerce assistant widget.
- It is available across main customer pages.
- It is not a separate tab.

## Phase 6 - Remove Or Move Ops

Ops means internal demo operations:

- Reload products.
- Sync AI products.
- Rebuild embeddings.
- Show seed command hints.

Fix:

- Remove `Ops` from public/customer nav.
- Move it to `/admin` or `/admin/tools`.
- Label it `Admin Tools` or `Demo Tools`.
- Keep it hidden unless needed for demo.

Definition of done:

- Customer-facing nav has no `Ops`.
- Internal tools still exist somewhere intentional.

## Neo4j Demo Query Notes

Neo4j interaction tracking does not need changes in this pass. For demos, use a larger limit or query by the current logged-in user id. Browser results can look unchanged if the query limit is too small.

Useful queries:

```cypher
MATCH (u:User)-[r:VIEWED|ADDED_TO_CART|PURCHASED|RATED]->(p:Product)
RETURN u.id, type(r), p.id, p.name, r.count
ORDER BY r.updated_at DESC
LIMIT 200;
```

```cypher
MATCH (u:User {id: $user_id})-[r]->(p:Product)
RETURN u, r, p;
```

## Implementation Order

1. Fix Product API category response.
2. Add route-based frontend architecture.
3. Rebuild page components around routes.
4. Replace bookstore copy with generic ecommerce copy.
5. Fix category chips and empty states.
6. Add account/address page.
7. Update checkout to use saved address.
8. Convert Assistant into floating chat widget.
9. Move Ops to admin/demo tools route.
10. Rebuild Docker and run full flow.
11. Verify Neo4j with larger-limit Cypher queries.
12. Commit as a routing/profile/UI fix.

## Verification Checklist

```text
docker compose config --quiet
docker compose up -d --build
docker compose exec -T product_service python manage.py seed_products
docker compose exec -T ai_service python manage.py seed_graph_demo
```

Manual:

1. Open `/`.
2. Navigate to `/products`.
3. Click a product and verify URL `/products/:id`.
4. Click category chips; names display correctly and no blank page occurs.
5. Register/login.
6. Add delivery address in `/account`.
7. Checkout using saved address.
8. Use floating assistant.
9. Add to cart, view detail, checkout, review.
10. Rerun larger-limit Neo4j query and verify relationships/counts changed.
