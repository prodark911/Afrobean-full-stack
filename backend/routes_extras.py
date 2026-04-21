"""New features: postcode geocoding, review submission, back-in-stock alerts, auto-replenishment."""
import os, math
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Header, Depends
import httpx

from db import products, reviews, customers, orders, audit_logs
from db import db as mongo_db
from models import new_id, utcnow_iso
from auth import require_customer, get_current_user, require_admin

router = APIRouter(prefix="/api")

# Extra collections
back_in_stock_subs = mongo_db.back_in_stock_subs

# Afrobean store coordinates (1227 Bourges Blvd, Peterborough PE1 2AU)
STORE_LAT = 52.5854
STORE_LNG = -0.2452


def haversine_miles(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in miles."""
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


# ---------------- POSTCODE LOOKUP ----------------
@router.get("/postcode/lookup")
async def postcode_lookup(postcode: str):
    """Look up a UK postcode via postcodes.io and return distance from store (miles)."""
    pc = postcode.strip().replace(" ", "").upper()
    if not pc:
        raise HTTPException(400, "Postcode required")
    url = f"https://api.postcodes.io/postcodes/{pc}"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url)
    except Exception as e:
        raise HTTPException(503, f"Postcode service unavailable: {str(e)[:100]}")
    if r.status_code != 200:
        raise HTTPException(404, "Postcode not found")
    data = r.json()
    res = data.get("result") or {}
    lat = res.get("latitude")
    lng = res.get("longitude")
    if lat is None or lng is None:
        raise HTTPException(404, "Postcode has no coordinates")
    distance = round(haversine_miles(STORE_LAT, STORE_LNG, lat, lng), 2)
    return {
        "postcode": res.get("postcode", pc),
        "lat": lat, "lng": lng,
        "town": res.get("admin_district") or res.get("parish") or "",
        "country": res.get("country", "UK"),
        "region": res.get("region", ""),
        "distance_miles": distance,
        "within_radius": distance <= float(os.environ.get("DELIVERY_RADIUS_MILES", 5)),
    }


# ---------------- REVIEW SUBMISSION ----------------
@router.post("/reviews")
async def submit_review(data: Dict[str, Any], authorization: Optional[str] = Header(None)):
    """Customer-facing review submission. Works for both guest (requires email) and auth."""
    payload = await get_current_user(authorization)
    product_id = data.get("product_id")
    if not product_id:
        raise HTTPException(400, "product_id required")
    p = await products.find_one({"id": product_id}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Product not found")
    rating = int(data.get("rating", 5))
    rating = max(1, min(5, rating))
    title = (data.get("title") or "").strip()[:120]
    body = (data.get("body") or "").strip()[:2000]
    name = (data.get("customer_name") or "").strip()[:80]
    cid = None
    if payload and payload.get("type") == "customer":
        cid = payload["sub"]
        cust = await customers.find_one({"id": cid}, {"_id": 0, "name": 1, "email": 1})
        if cust:
            name = name or cust.get("name") or cust.get("email")
    if not name:
        raise HTTPException(400, "Your name is required")
    if not body:
        raise HTTPException(400, "Review body is required")

    # Verified purchase check
    verified = False
    if cid:
        ord_cnt = await orders.count_documents({
            "customer_id": cid, "payment_status": "paid",
            "items.product_id": product_id,
        })
        verified = ord_cnt > 0

    doc = {
        "id": new_id(), "product_id": product_id, "customer_id": cid,
        "customer_name": name, "rating": rating, "title": title, "body": body,
        "verified": verified, "created_at": utcnow_iso(),
    }
    await reviews.insert_one(doc)

    # Update product avg rating + count
    agg = await reviews.aggregate([
        {"$match": {"product_id": product_id}},
        {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]).to_list(1)
    if agg:
        await products.update_one({"id": product_id},
            {"$set": {"avg_rating": round(agg[0]["avg"], 2), "review_count": agg[0]["count"]}})

    doc.pop("_id", None)
    return doc


# ---------------- BACK-IN-STOCK ----------------
@router.post("/back-in-stock/subscribe")
async def subscribe_back_in_stock(data: Dict[str, Any], authorization: Optional[str] = Header(None)):
    """Subscribe an email to be notified when a product is back in stock."""
    email = (data.get("email") or "").strip().lower()
    product_id = data.get("product_id")
    if not email or not product_id:
        raise HTTPException(400, "email and product_id required")
    p = await products.find_one({"id": product_id}, {"_id": 0, "name": 1, "stock": 1})
    if not p:
        raise HTTPException(404, "Product not found")
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    existing = await back_in_stock_subs.find_one({"email": email, "product_id": product_id, "notified": False})
    if existing:
        return {"ok": True, "already_subscribed": True}
    await back_in_stock_subs.insert_one({
        "id": new_id(), "email": email, "product_id": product_id,
        "customer_id": cid, "notified": False, "created_at": utcnow_iso(),
    })
    return {"ok": True, "subscribed": True,
            "message": f"We'll email {email} when {p['name']} is back in stock."}


@router.get("/admin/back-in-stock")
async def admin_list_bis(payload=Depends(require_admin)):
    """Admin view of back-in-stock subscriptions."""
    subs = await back_in_stock_subs.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    # Hydrate product names
    pids = list({s["product_id"] for s in subs})
    prods = await products.find({"id": {"$in": pids}}, {"_id": 0, "id": 1, "name": 1, "stock": 1}).to_list(500)
    pmap = {p["id"]: p for p in prods}
    for s in subs:
        s["product"] = pmap.get(s["product_id"])
    return subs


@router.post("/admin/back-in-stock/trigger")
async def admin_trigger_bis_alerts(payload=Depends(require_admin)):
    """Scan subs and mark those whose products are back in stock — queues email notifications."""
    queued = 0
    async for sub in back_in_stock_subs.find({"notified": False}):
        p = await products.find_one({"id": sub["product_id"]}, {"_id": 0, "name": 1, "stock": 1})
        if p and p.get("stock", 0) > 0:
            await back_in_stock_subs.update_one(
                {"id": sub["id"]},
                {"$set": {"notified": True, "notified_at": utcnow_iso()}},
            )
            # Log in audit (actual email sending is the readiness layer — stored template
            # would be rendered and sent by Resend/SendGrid when connected)
            await audit_logs.insert_one({
                "id": new_id(), "actor_email": payload.get("email"), "actor_role": payload.get("role"),
                "action": "back_in_stock.notify_queued", "target_type": "product",
                "target_id": sub["product_id"],
                "changes": {"email": sub["email"], "product": p.get("name")},
                "ip": None, "created_at": utcnow_iso(),
            })
            queued += 1
    return {"queued": queued}


# ---------------- AUTO-REPLENISHMENT ----------------
@router.patch("/me/auto-replenishment")
async def set_auto_replenishment(data: Dict[str, Any], payload=Depends(require_customer)):
    enabled = bool(data.get("enabled"))
    interval_days = int(data.get("interval_days", 30))
    interval_days = max(7, min(180, interval_days))
    await customers.update_one({"id": payload["sub"]}, {
        "$set": {"auto_replenishment": enabled, "replenishment_interval_days": interval_days}
    })
    return {"auto_replenishment": enabled, "replenishment_interval_days": interval_days}


@router.get("/admin/replenishment/due")
async def admin_replenishment_due(payload=Depends(require_admin)):
    """List customers due for a replenishment reminder/order."""
    # customers with auto_replenishment=True and last paid order > interval_days ago
    out = []
    cursor = customers.find({"auto_replenishment": True}, {"_id": 0})
    async for c in cursor:
        interval = int(c.get("replenishment_interval_days", 30))
        cutoff = (datetime.now(timezone.utc) - timedelta(days=interval)).isoformat()
        last = await orders.find_one({"customer_id": c["id"], "payment_status": "paid"},
                                     {"_id": 0, "created_at": 1, "order_number": 1},
                                     sort=[("created_at", -1)])
        if last and last["created_at"] < cutoff:
            out.append({
                "customer_id": c["id"], "email": c["email"], "name": c.get("name"),
                "interval_days": interval, "last_order": last,
                "days_since_last_order": (datetime.now(timezone.utc) - datetime.fromisoformat(last["created_at"])).days,
            })
    return out
