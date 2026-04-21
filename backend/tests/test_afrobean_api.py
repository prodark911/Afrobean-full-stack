"""Afrobean backend API integration tests."""
import os
import uuid
import pytest
import requests

BASE = os.environ.get("REACT_APP_BACKEND_URL", "https://7ecb0ad9-9094-4df5-b9c9-0b0cfc2137f3.preview.emergentagent.com").rstrip("/")
API = f"{BASE}/api"

ADMIN_EMAIL = "admin@afrobean.co.uk"
ADMIN_PASS = "Admin@123"
CUSTOMER_EMAIL = "demo@afrobean.co.uk"
CUSTOMER_PASS = "Demo@123"


@pytest.fixture(scope="session")
def s():
    return requests.Session()


@pytest.fixture(scope="session")
def admin_token(s):
    r = s.post(f"{API}/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="session")
def customer_token(s):
    r = s.post(f"{API}/auth/login", json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASS})
    if r.status_code != 200:
        pytest.skip(f"Customer login failed: {r.text}")
    return r.json()["token"]


@pytest.fixture(scope="session")
def guest_session_id():
    return str(uuid.uuid4())


# ---------------- Public catalog ----------------
class TestCatalog:
    def test_health(self, s):
        r = s.get(f"{API}/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_store_info(self, s):
        r = s.get(f"{API}/store-info")
        assert r.status_code == 200
        data = r.json()
        assert data["currency"] == "GBP"
        assert data["free_delivery_threshold"] == 50

    def test_categories(self, s):
        r = s.get(f"{API}/categories")
        assert r.status_code == 200
        cats = r.json()
        assert isinstance(cats, list) and len(cats) > 0
        assert "slug" in cats[0] and "product_count" in cats[0]

    def test_products(self, s):
        r = s.get(f"{API}/products")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data and "total" in data
        assert data["total"] > 0

    def test_products_peterborough_market(self, s):
        r = s.get(f"{API}/products/peterborough-market")
        # either a product slug or 404
        assert r.status_code in (200, 404)

    def test_meal_collections(self, s):
        r = s.get(f"{API}/meal-collections")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and len(data) > 0

    def test_meal_collection_jollof(self, s):
        r = s.get(f"{API}/meal-collections/jollof-rice-essentials")
        assert r.status_code == 200
        data = r.json()
        assert "meal_collection" in data and "products" in data

    def test_bundles(self, s):
        r = s.get(f"{API}/bundles")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_collection_best_sellers(self, s):
        r = s.get(f"{API}/collections/best-sellers")
        assert r.status_code == 200
        data = r.json()
        assert "collection" in data and "products" in data

    def test_category_rice(self, s):
        r = s.get(f"{API}/categories/rice-flour-swallows")
        assert r.status_code == 200
        data = r.json()
        assert "category" in data and "products" in data


# ---------------- Customer auth ----------------
class TestAuth:
    def test_signup_new_user(self, s):
        email = f"TEST_{uuid.uuid4().hex[:8]}@afrobean-test.co.uk"
        r = s.post(f"{API}/auth/signup", json={"email": email, "password": "Test@1234", "name": "Test User"})
        assert r.status_code == 200, r.text
        assert "token" in r.json()

    def test_login_demo(self, s):
        r = s.post(f"{API}/auth/login", json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASS})
        assert r.status_code == 200, r.text
        assert "token" in r.json()

    def test_login_invalid(self, s):
        r = s.post(f"{API}/auth/login", json={"email": CUSTOMER_EMAIL, "password": "wrong"})
        assert r.status_code == 401

    def test_me_requires_auth(self, s):
        r = s.get(f"{API}/me")
        assert r.status_code in (401, 403)

    def test_me_with_token(self, s, customer_token):
        r = s.get(f"{API}/me", headers={"Authorization": f"Bearer {customer_token}"})
        assert r.status_code == 200
        assert r.json()["email"] == CUSTOMER_EMAIL

    def test_otp_flow(self, s):
        email = f"test_otp_{uuid.uuid4().hex[:6]}@example.com"
        r = s.post(f"{API}/auth/otp/request", json={"email": email})
        assert r.status_code == 200
        code = r.json().get("dev_code")
        assert code and len(code) == 6
        r2 = s.post(f"{API}/auth/otp/verify", json={"email": email, "code": code})
        assert r2.status_code == 200
        assert "token" in r2.json()

    def test_otp_invalid_code(self, s):
        email = f"test_otp_{uuid.uuid4().hex[:6]}@example.com"
        s.post(f"{API}/auth/otp/request", json={"email": email})
        r = s.post(f"{API}/auth/otp/verify", json={"email": email, "code": "000000"})
        assert r.status_code == 401


# ---------------- Cart & Delivery ----------------
class TestCart:
    def test_delivery_quote_free(self, s):
        r = s.post(f"{API}/delivery/quote", json={"subtotal": 60, "distance_miles": 2})
        assert r.status_code == 200
        data = r.json()
        assert data["available"] is True
        assert data["fee"] == 0

    def test_delivery_quote_paid(self, s):
        r = s.post(f"{API}/delivery/quote", json={"subtotal": 20, "distance_miles": 2})
        assert r.status_code == 200
        assert r.json()["fee"] == round(2.99 * 2, 2)

    def test_delivery_quote_out_of_range(self, s):
        r = s.post(f"{API}/delivery/quote", json={"subtotal": 20, "distance_miles": 10})
        assert r.status_code == 200
        assert r.json()["available"] is False

    def test_guest_cart_add_update_clear(self, s, guest_session_id):
        # get a product id
        prods = s.get(f"{API}/products").json()["items"]
        assert prods
        pid = prods[0]["id"]
        r = s.post(f"{API}/cart/add", params={"session_id": guest_session_id},
                   json={"product_id": pid, "quantity": 2})
        assert r.status_code == 200, r.text
        data = r.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2

        # update
        vsku = data["items"][0].get("variant_sku")
        r2 = s.post(f"{API}/cart/update", params={"session_id": guest_session_id},
                    json={"product_id": pid, "variant_sku": vsku, "quantity": 3})
        assert r2.status_code == 200
        assert r2.json()["items"][0]["quantity"] == 3

        # clear
        r3 = s.post(f"{API}/cart/clear", params={"session_id": guest_session_id})
        assert r3.status_code == 200

        # verify cleared
        r4 = s.get(f"{API}/cart", params={"session_id": guest_session_id})
        assert r4.status_code == 200
        assert r4.json()["items"] == []

    def test_cart_bulk_add(self, s):
        sid = str(uuid.uuid4())
        prods = s.get(f"{API}/products").json()["items"][:3]
        items = [{"product_id": p["id"], "quantity": 1} for p in prods]
        r = s.post(f"{API}/cart/bulk-add", params={"session_id": sid}, json={"items": items})
        assert r.status_code == 200
        assert len(r.json()["items"]) == len(items)


# ---------------- Wishlist ----------------
class TestWishlist:
    def test_wishlist_requires_auth(self, s):
        r = s.get(f"{API}/wishlist")
        assert r.status_code in (401, 403)

    def test_wishlist_toggle(self, s, customer_token):
        headers = {"Authorization": f"Bearer {customer_token}"}
        prods = s.get(f"{API}/products").json()["items"]
        pid = prods[0]["id"]
        r = s.post(f"{API}/wishlist/toggle", headers=headers, json={"product_id": pid})
        assert r.status_code == 200
        assert pid in r.json()["product_ids"]
        # toggle again removes
        r2 = s.post(f"{API}/wishlist/toggle", headers=headers, json={"product_id": pid})
        assert r2.status_code == 200
        assert pid not in r2.json()["product_ids"]


# ---------------- AI ----------------
class TestAI:
    def test_ai_chat_jollof(self, s):
        r = s.post(f"{API}/ai/chat", json={"message": "jollof rice for 5 people"}, timeout=90)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "session_id" in data
        assert "reply" in data
        # Basket may or may not be produced depending on model output but should be valid type
        assert data["basket"] is None or isinstance(data["basket"], dict)
        # Store for next test
        pytest.ai_session_id = data["session_id"]
        pytest.ai_basket = data["basket"]

    def test_ai_add_to_cart(self, s):
        sid = getattr(pytest, "ai_session_id", None)
        basket = getattr(pytest, "ai_basket", None)
        if not sid or not basket or not basket.get("hydrated_items"):
            pytest.skip("AI did not produce a basket to add")
        cart_sid = str(uuid.uuid4())
        r = s.post(f"{API}/ai/sessions/{sid}/add-to-cart", json={"cart_session_id": cart_sid})
        assert r.status_code == 200


# ---------------- Admin ----------------
class TestAdmin:
    def test_admin_login(self, s):
        r = s.post(f"{API}/admin/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_admin_me(self, s, admin_token):
        r = s.get(f"{API}/admin/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert r.json()["email"] == ADMIN_EMAIL

    def test_dashboard(self, s, admin_token):
        r = s.get(f"{API}/admin/dashboard", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        for k in ["sales", "orders_by_status", "top_products", "totals"]:
            assert k in data

    def test_admin_products(self, s, admin_token):
        r = s.get(f"{API}/admin/products", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        assert "items" in data and data["total"] > 0

    def test_admin_product_crud(self, s, admin_token):
        h = {"Authorization": f"Bearer {admin_token}"}
        slug = f"test-{uuid.uuid4().hex[:6]}"
        r = s.post(f"{API}/admin/products", headers=h,
                   json={"name": "TEST Product", "slug": slug, "price": 9.99, "status": "draft"})
        assert r.status_code == 200
        pid = r.json()["id"]
        # patch
        r2 = s.patch(f"{API}/admin/products/{pid}", headers=h, json={"price": 12.50})
        assert r2.status_code == 200
        assert r2.json()["price"] == 12.50
        # bulk publish
        r3 = s.post(f"{API}/admin/products/bulk", headers=h,
                    json={"ids": [pid], "action": "publish"})
        assert r3.status_code == 200
        assert r3.json()["count"] == 1
        # archive
        r4 = s.delete(f"{API}/admin/products/{pid}", headers=h)
        assert r4.status_code == 200

    def test_admin_categories_list(self, s, admin_token):
        r = s.get(f"{API}/admin/categories", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_admin_collections(self, s, admin_token):
        r = s.get(f"{API}/admin/collections", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_admin_meal_collections(self, s, admin_token):
        h = {"Authorization": f"Bearer {admin_token}"}
        r = s.get(f"{API}/admin/meal-collections", headers=h)
        assert r.status_code == 200
        assert len(r.json()) > 0
        mc_id = r.json()[0]["id"]
        # preview basket
        r2 = s.post(f"{API}/admin/meal-collections/{mc_id}/preview-basket", headers=h, json={})
        assert r2.status_code == 200
        data = r2.json()
        assert "basket" in data and "total" in data

    def test_admin_bundles(self, s, admin_token):
        r = s.get(f"{API}/admin/bundles", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200

    def test_admin_orders(self, s, admin_token):
        r = s.get(f"{API}/admin/orders", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert "items" in r.json()

    def test_admin_customers(self, s, admin_token):
        r = s.get(f"{API}/admin/customers", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert "items" in r.json()

    def test_admin_inventory(self, s, admin_token):
        h = {"Authorization": f"Bearer {admin_token}"}
        r = s.get(f"{API}/admin/inventory", headers=h)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        # low stock filter
        r2 = s.get(f"{API}/admin/inventory", headers=h, params={"view": "low_stock"})
        assert r2.status_code == 200
        # adjust stock
        if items:
            pid = items[0]["id"]
            r3 = s.post(f"{API}/admin/inventory/adjust", headers=h,
                        json={"product_id": pid, "delta": 5, "reason": "test"})
            assert r3.status_code == 200
            assert "stock" in r3.json()

    def test_admin_messaging(self, s, admin_token):
        h = {"Authorization": f"Bearer {admin_token}"}
        r1 = s.get(f"{API}/admin/messaging/templates", headers=h)
        assert r1.status_code == 200
        r2 = s.get(f"{API}/admin/messaging/automations", headers=h)
        assert r2.status_code == 200

    def test_admin_analytics(self, s, admin_token):
        r = s.get(f"{API}/admin/analytics/overview",
                  headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        data = r.json()
        for k in ["by_category", "top_products", "total_revenue_30d", "order_count_30d"]:
            assert k in data

    def test_admin_audit_logs(self, s, admin_token):
        r = s.get(f"{API}/admin/audit-logs",
                  headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_admin_export_csv(self, s, admin_token):
        r = s.get(f"{API}/admin/exports/products",
                  headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert "text/csv" in r.headers.get("content-type", "")
        assert "name,slug" in r.text[:200]


# ---------------- Stripe Checkout ----------------
class TestCheckout:
    def test_create_checkout_session(self, s):
        sid = str(uuid.uuid4())
        prods = s.get(f"{API}/products").json()["items"]
        pid = prods[0]["id"]
        s.post(f"{API}/cart/add", params={"session_id": sid},
               json={"product_id": pid, "quantity": 1})
        payload = {
            "origin_url": BASE,
            "distance_miles": 2,
            "address": {
                "name": "Test User",
                "phone": "07700900123",
                "line1": "1 Test Street",
                "city": "Peterborough",
                "postcode": "PE1 1PY",
                "country": "UK",
            },
            "notes": "test",
        }
        r = s.post(f"{API}/checkout/session", params={"session_id": sid}, json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["url"].startswith("https://")
        assert "session_id" in data and "order_number" in data
        pytest.stripe_session_id = data["session_id"]

    def test_checkout_status(self, s):
        sid = getattr(pytest, "stripe_session_id", None)
        if not sid:
            pytest.skip("no session")
        r = s.get(f"{API}/checkout/status/{sid}")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("open", "complete", "expired")
