"""Shop routes: auth, customer, cart, wishlist, orders."""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, List, Dict, Any
import random
from db import customers, carts, orders, wishlists, products, clean
from models import (
    CustomerSignupRequest, CustomerLoginRequest, OTPRequest, OTPVerifyRequest,
    CartAddBody, Cart, new_id, utcnow_iso,
)
from auth import hash_password, verify_password, create_token, require_customer
from db import otp_codes

router = APIRouter(prefix="/api")


# --- Customer auth ---
@router.post("/auth/signup")
async def signup(body: CustomerSignupRequest):
    existing = await customers.find_one({"email": body.email})
    if existing:
        raise HTTPException(400, "Email already registered")
    doc = {
        "id": new_id(),
        "email": body.email, "name": body.name, "phone": body.phone or "",
        "password_hash": hash_password(body.password),
        "email_consent": True, "whatsapp_consent": False, "marketing_consent": False,
        "addresses": [],
        "created_at": utcnow_iso(),
        "active": True, "total_spend": 0, "order_count": 0,
    }
    await customers.insert_one(doc)
    token = create_token({"sub": doc["id"], "email": doc["email"], "type": "customer"})
    return {"token": token, "customer": {k: v for k, v in doc.items() if k not in ["_id", "password_hash"]}}


@router.post("/auth/login")
async def login(body: CustomerLoginRequest):
    user = await customers.find_one({"email": body.email}, {"_id": 0})
    if not user or not user.get("password_hash") or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    token = create_token({"sub": user["id"], "email": user["email"], "type": "customer"})
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "customer": safe}


@router.post("/auth/otp/request")
async def otp_request(body: OTPRequest):
    code = f"{random.randint(0, 999999):06d}"
    await otp_codes.update_one(
        {"email": body.email},
        {"$set": {"email": body.email, "code": code, "created_at": utcnow_iso()}},
        upsert=True,
    )
    # In prod this would be emailed. For demo we return in "dev_code".
    return {"ok": True, "dev_code": code, "message": "OTP sent (check email). Dev code shown for testing."}


@router.post("/auth/otp/verify")
async def otp_verify(body: OTPVerifyRequest):
    rec = await otp_codes.find_one({"email": body.email}, {"_id": 0})
    if not rec or rec.get("code") != body.code:
        raise HTTPException(401, "Invalid code")
    # Find or create customer
    user = await customers.find_one({"email": body.email}, {"_id": 0})
    if not user:
        user = {
            "id": new_id(), "email": body.email, "name": body.email.split("@")[0].title(),
            "phone": "", "password_hash": None,
            "email_consent": True, "whatsapp_consent": False, "marketing_consent": False,
            "addresses": [], "created_at": utcnow_iso(), "active": True,
            "total_spend": 0, "order_count": 0,
        }
        await customers.insert_one(user)
        user = {k: v for k, v in user.items() if k != "_id"}
    await otp_codes.delete_one({"email": body.email})
    token = create_token({"sub": user["id"], "email": user["email"], "type": "customer"})
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "customer": safe}


@router.get("/me")
async def me(payload=Depends(require_customer)):
    user = await customers.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(404, "Not found")
    return user


@router.patch("/me")
async def update_me(data: Dict[str, Any], payload=Depends(require_customer)):
    allowed = {"name", "phone", "addresses", "marketing_consent", "whatsapp_consent", "email_consent"}
    update = {k: v for k, v in data.items() if k in allowed}
    if update:
        await customers.update_one({"id": payload["sub"]}, {"$set": update})
    return await customers.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})


# --- Cart ---
async def _get_or_create_cart(customer_id: Optional[str], session_id: Optional[str]):
    q = {}
    if customer_id:
        q["customer_id"] = customer_id
    elif session_id:
        q["session_id"] = session_id
    else:
        return None
    cart = await carts.find_one(q, {"_id": 0})
    if not cart:
        cart = {"id": new_id(), "customer_id": customer_id, "session_id": session_id,
                "items": [], "coupon": None, "notes": "", "updated_at": utcnow_iso()}
        await carts.insert_one(cart)
        cart = {k: v for k, v in cart.items() if k != "_id"}
    return cart


@router.get("/cart")
async def get_cart(session_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    from auth import get_current_user
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    cart = await _get_or_create_cart(cid, session_id)
    if not cart:
        return {"id": None, "items": [], "subtotal": 0}
    subtotal = sum(i["price"] * i["quantity"] for i in cart["items"])
    cart["subtotal"] = round(subtotal, 2)
    return cart


@router.post("/cart/add")
async def add_to_cart(body: CartAddBody, session_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    from auth import get_current_user
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    cart = await _get_or_create_cart(cid, session_id or new_id())
    prod = await products.find_one({"id": body.product_id, "status": "active"}, {"_id": 0})
    if not prod:
        raise HTTPException(404, "Product not found")
    # Find variant
    variant = None
    if body.variant_sku:
        for v in prod["variants"]:
            if v["sku"] == body.variant_sku:
                variant = v
                break
    if not variant:
        variant = next((v for v in prod["variants"] if v.get("is_default")), prod["variants"][0] if prod["variants"] else None)
    price = variant["price"] if variant else prod["price"]
    size_label = variant["size_label"] if variant else None
    variant_sku = variant["sku"] if variant else None

    # Merge if same item already in cart
    items = cart["items"]
    merged = False
    for it in items:
        if it["product_id"] == body.product_id and it.get("variant_sku") == variant_sku:
            it["quantity"] += body.quantity
            merged = True
            break
    if not merged:
        items.append({
            "product_id": body.product_id,
            "variant_sku": variant_sku,
            "quantity": body.quantity,
            "price": price,
            "name": prod["name"],
            "image": prod["images"][0] if prod.get("images") else None,
            "size_label": size_label,
        })
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": items, "updated_at": utcnow_iso()}})
    return await get_cart(session_id=cart.get("session_id"), authorization=authorization)


@router.post("/cart/update")
async def update_cart_item(data: Dict[str, Any], session_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    from auth import get_current_user
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    cart = await _get_or_create_cart(cid, session_id)
    if not cart:
        raise HTTPException(404, "Cart not found")
    product_id = data.get("product_id")
    variant_sku = data.get("variant_sku")
    qty = int(data.get("quantity", 0))
    items = cart["items"]
    new_items = []
    for it in items:
        if it["product_id"] == product_id and it.get("variant_sku") == variant_sku:
            if qty > 0:
                it["quantity"] = qty
                new_items.append(it)
            # else: remove
        else:
            new_items.append(it)
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": new_items, "updated_at": utcnow_iso()}})
    return await get_cart(session_id=cart.get("session_id"), authorization=authorization)


@router.post("/cart/clear")
async def clear_cart(session_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    from auth import get_current_user
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    cart = await _get_or_create_cart(cid, session_id)
    if not cart:
        return {"ok": True}
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": [], "updated_at": utcnow_iso()}})
    return {"ok": True}


@router.post("/cart/bulk-add")
async def bulk_add(data: Dict[str, Any], session_id: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Add an entire list of product_ids or {product_id, variant_sku, quantity} to cart (for meal collections)."""
    from auth import get_current_user
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    items_to_add = data.get("items", [])
    cart = await _get_or_create_cart(cid, session_id or new_id())
    for item in items_to_add:
        pid = item.get("product_id")
        qty = int(item.get("quantity", 1))
        vsku = item.get("variant_sku")
        prod = await products.find_one({"id": pid, "status": "active"}, {"_id": 0})
        if not prod:
            continue
        variant = None
        if vsku:
            variant = next((v for v in prod["variants"] if v["sku"] == vsku), None)
        if not variant:
            variant = next((v for v in prod["variants"] if v.get("is_default")), prod["variants"][0] if prod["variants"] else None)
        price = variant["price"] if variant else prod["price"]
        items = cart["items"]
        merged = False
        for it in items:
            if it["product_id"] == pid and it.get("variant_sku") == (variant["sku"] if variant else None):
                it["quantity"] += qty
                merged = True
                break
        if not merged:
            items.append({
                "product_id": pid,
                "variant_sku": variant["sku"] if variant else None,
                "quantity": qty,
                "price": price,
                "name": prod["name"],
                "image": prod["images"][0] if prod.get("images") else None,
                "size_label": variant["size_label"] if variant else None,
            })
        cart["items"] = items
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": cart["items"], "updated_at": utcnow_iso()}})
    return await get_cart(session_id=cart.get("session_id"), authorization=authorization)


# --- Wishlist ---
@router.get("/wishlist")
async def get_wishlist(payload=Depends(require_customer)):
    wl = await wishlists.find_one({"customer_id": payload["sub"]}, {"_id": 0})
    if not wl:
        return {"product_ids": [], "products": []}
    prods = await products.find({"id": {"$in": wl["product_ids"]}, "status": "active"}, {"_id": 0}).to_list(100)
    return {"product_ids": wl["product_ids"], "products": prods}


@router.post("/wishlist/toggle")
async def toggle_wishlist(data: Dict[str, Any], payload=Depends(require_customer)):
    pid = data.get("product_id")
    wl = await wishlists.find_one({"customer_id": payload["sub"]}, {"_id": 0})
    if not wl:
        wl = {"id": new_id(), "customer_id": payload["sub"], "product_ids": [pid], "updated_at": utcnow_iso()}
        await wishlists.insert_one(wl)
    else:
        ids = wl["product_ids"]
        if pid in ids:
            ids.remove(pid)
        else:
            ids.append(pid)
        await wishlists.update_one({"id": wl["id"]}, {"$set": {"product_ids": ids, "updated_at": utcnow_iso()}})
    return await get_wishlist(payload)


# --- Orders (customer-facing) ---
@router.get("/orders")
async def my_orders(payload=Depends(require_customer)):
    docs = await orders.find({"customer_id": payload["sub"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return docs


@router.get("/orders/{order_number}")
async def my_order(order_number: str, payload=Depends(require_customer)):
    o = await orders.find_one({"order_number": order_number, "customer_id": payload["sub"]}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Order not found")
    return o


@router.post("/orders/{order_number}/reorder")
async def reorder(order_number: str, payload=Depends(require_customer)):
    o = await orders.find_one({"order_number": order_number, "customer_id": payload["sub"]}, {"_id": 0})
    if not o:
        raise HTTPException(404, "Order not found")
    cart = await _get_or_create_cart(payload["sub"], None)
    for it in o["items"]:
        # Simple merge
        existing = next((c for c in cart["items"] if c["product_id"] == it["product_id"] and c.get("variant_sku") == it.get("variant_sku")), None)
        if existing:
            existing["quantity"] += it["quantity"]
        else:
            cart["items"].append(dict(it))
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": cart["items"], "updated_at": utcnow_iso()}})
    return {"ok": True, "cart_id": cart["id"]}


# --- Delivery quote ---
@router.post("/delivery/quote")
async def delivery_quote(data: Dict[str, Any]):
    """Calculate delivery fee. Expects {subtotal, distance_miles}."""
    import os
    subtotal = float(data.get("subtotal", 0))
    distance = float(data.get("distance_miles", 0))
    per_mile = float(os.environ.get("DELIVERY_PER_MILE", 2.99))
    free_threshold = float(os.environ.get("FREE_DELIVERY_THRESHOLD", 50))
    radius = float(os.environ.get("DELIVERY_RADIUS_MILES", 5))
    if distance > radius:
        return {"available": False, "reason": f"We only deliver within {radius} miles of 1227 Bourges Blvd, Peterborough PE1 2AU."}
    fee = round(per_mile * max(distance, 0), 2)
    if subtotal >= free_threshold:
        fee = 0
    return {"available": True, "fee": fee, "free_threshold": free_threshold, "radius_miles": radius,
            "per_mile_fee": per_mile,
            "away_from_free": round(max(0, free_threshold - subtotal), 2)}
