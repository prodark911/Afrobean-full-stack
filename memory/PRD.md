# Afrobean — PRD & Build Log

## Original Problem Statement
Build a production-ready full-stack ecommerce platform called Afrobean — a premium African online supermarket based in Peterborough, UK. The platform includes a premium customer-facing storefront, an AI meal-to-cart shopping assistant, an organised admin backend, structured catalogue and collection management, bundle/upsell/pack-size logic, order/customer/inventory management, WhatsApp and email automation readiness, and analytics/reporting.

**Currency:** GBP (£). **Location:** 1227 Bourges Blvd, Peterborough PE1 2AU. **Delivery:** free over £50, otherwise £2.99/mile within 5 miles.

## User Choices
- **AI model:** GPT-5.2 (OpenAI) via Emergent Universal LLM Key
- **Stripe:** test key (`sk_test_emergent`) pre-configured in pod env
- **Stack:** React + FastAPI + MongoDB (equivalent architecture to requested Next.js+Postgres)
- **WhatsApp/email:** readiness layer (UI + DB), not live sending
- **Seed:** `admin@afrobean.co.uk / Admin@123` (super admin), `demo@afrobean.co.uk / Demo@123` (customer)

## Architecture
- **Backend** (FastAPI + MongoDB, /app/backend):
  - `server.py` — app entry, mounts routers, seeds on startup
  - `models.py` — Pydantic models for all entities
  - `auth.py` — JWT auth, password hashing, admin/customer guards
  - `db.py` — Mongo client, collections, indexes
  - `seed.py` — seeds ~68 products, 12 categories, 6 meal collections, 7 bundles, 5 collections, 8 templates, 7 automations, delivery zone, reviews
  - `routes_catalog.py` — products, categories, collections, meal-collections, bundles, reviews
  - `routes_shop.py` — signup/login/OTP, me, cart (guest+auth), wishlist, orders, delivery quote
  - `routes_admin.py` — admin auth, dashboard, products CRUD + bulk, categories/collections CRUD, meal mapping edit + preview, bundles, inventory views + adjust, orders list+detail+patch, customers, messaging templates+automations, analytics, audit logs, delivery zones, admin users, CSV imports/exports
  - `routes_ai.py` — GPT-5.2 chat with `<basket>` JSON extraction, multi-turn session persistence, add-to-cart from AI basket
  - `routes_stripe.py` — Checkout session creation, status polling (with graceful fallback for emergent test proxy), webhook handler

- **Frontend** (React + Tailwind, /app/frontend/src):
  - Design: Playfair Display (display) + Outfit (body) + IBM Plex Sans (admin). Deep terracotta (#8C3219) + warm ivory (#FDFBF7) + forest green accents.
  - Storefront layout: announcement bar, secondary tagline bar, sticky header with search + AI CTA + cart drawer, mega nav, footer with newsletter + floating WhatsApp
  - Admin layout: dark sidebar with 17 modules, top topbar, table-driven pages, modals

## Pages Implemented
### Storefront (19)
Home (10+ sections: hero, categories grid, AI callout, best sellers, meal collections, free delivery banner, bundles, why-shop, recipes, new arrivals, reviews, WhatsApp, final CTA), Shop All, Category, Collection, Meal Collection index, Meal Collection detail (with slot customisation + add-all), PDP (variants, wishlist, reviews, related), Search, AI Assistant (chat with basket panel), Cart page, Cart drawer, Checkout (address + distance + Stripe), Checkout Success (polling), Login (password + OTP + signup tabs), Account (overview/orders/wishlist/details), About, Delivery, FAQ, Contact.

### Admin (18)
Login, Dashboard (sales today/week/month, AOV, repeat rate, orders by status, low stock, top products, meal performance, recent orders, AI sessions), Products (list + bulk + edit + create), Categories, Collections, Meal Collections, AI Mapping (per-slot default/substitute product editor + preview), Bundles, Pricing (margin view, missing cost highlight), Inventory (all/low/out/fast/dead + adjust), Orders (list + detail with timeline + status updates), Customers, Messaging (templates + automation toggles), Content, Analytics (sales by category + top products + 30d revenue), Imports/Exports (CSV), Delivery Zones, Audit Logs, Settings & Roles.

## Integrations
- **GPT-5.2** via `emergentintegrations.llm.chat.LlmChat` → returns `<basket>JSON</basket>` parsed into hydrated cart items.
- **Stripe Checkout** via `emergentintegrations.payments.stripe.checkout` for session creation + webhook. Status endpoint uses graceful fallback to stored txn state (emergent test proxy doesn't support retrieve).

## Testing
- Iteration 1 (/app/test_reports/iteration_1.json):
  - Backend: 43/44 pytest tests passing (single bug: checkout-status 500 → FIXED with graceful fallback)
  - Frontend: all core flows verified (Home, Category, Collection, PDP + cart drawer, Meal collection, Cart, Login, Admin login → dashboard, full AI assistant chat → basket → add to cart)

## Next Action Items / Backlog
- P1: Wire live WhatsApp (Twilio) + email (Resend/SendGrid) when customer provides API keys
- P1: Real geocoding for postcode → miles (currently user-entered)
- P2: Saved addresses UX on account page (backend supports, UI minimal)
- P2: Reviews submission flow for customers
- P2: Smart collections rules engine
- P2: Stripe live key + subscription/auto-replenishment

## Credentials
See `/app/memory/test_credentials.md`.
