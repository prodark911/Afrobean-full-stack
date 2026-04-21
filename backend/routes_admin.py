"""Admin routes: auth, dashboard, products CRUD, categories CRUD, collections, meal mappings,
bundles, inventory, orders, customers, messaging, analytics, audit logs, imports, delivery."""
import os
import csv
import io
from fastapi import APIRouter, HTTPException, Depends, Header, Query, UploadFile, File
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from db import (
    admin_users, customers, categories, products, collections_col, meal_collections,
    bundles, orders, audit_logs, message_templates, automation_flows, delivery_zones,
    carts, ai_sessions, reviews, imports,
)
from models import (
    AdminLoginRequest, new_id, utcnow_iso,
)
from auth import hash_password, verify_password, create_token, require_admin, require_role

router = APIRouter(prefix="/api/admin")


async def log_audit(actor, action, target_type=None, target_id=None, changes=None):
    await audit_logs.insert_one({
        "id": new_id(),
        "actor_email": actor.get("email") if actor else None,
        "actor_role": actor.get("role") if actor else None,
        "action": action, "target_type": target_type, "target_id": target_id,
        "changes": changes, "ip": None,
        "created_at": utcnow_iso(),
    })


# --- Admin Auth ---
@router.post("/auth/login")
async def admin_login(body: AdminLoginRequest):
    user = await admin_users.find_one({"email": body.email, "active": True}, {"_id": 0})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_token({"sub": user["id"], "email": user["email"], "role": user["role"], "type": "admin"})
    await log_audit(user, "admin.login")
    return {"token": token, "user": {k: v for k, v in user.items() if k != "password_hash"}}


@router.get("/me")
async def admin_me(payload=Depends(require_admin)):
    user = await admin_users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    return user


# --- Dashboard ---
@router.get("/dashboard")
async def admin_dashboard(payload=Depends(require_admin)):
    now = datetime.now(timezone.utc)
    today_iso = now.date().isoformat()
    week_ago = (now - timedelta(days=7)).isoformat()
    month_ago = (now - timedelta(days=30)).isoformat()

    paid_today = await orders.find({"payment_status": "paid", "created_at": {"$gte": today_iso}}, {"_id": 0}).to_list(1000)
    paid_week = await orders.find({"payment_status": "paid", "created_at": {"$gte": week_ago}}, {"_id": 0}).to_list(5000)
    paid_month = await orders.find({"payment_status": "paid", "created_at": {"$gte": month_ago}}, {"_id": 0}).to_list(10000)

    sum_today = sum(o["total"] for o in paid_today)
    sum_week = sum(o["total"] for o in paid_week)
    sum_month = sum(o["total"] for o in paid_month)
    aov = round(sum_month / len(paid_month), 2) if paid_month else 0

    # repeat rate
    customer_order_counts = {}
    for o in paid_month:
        cid = o.get("customer_id")
        if cid:
            customer_order_counts[cid] = customer_order_counts.get(cid, 0) + 1
    repeat = sum(1 for v in customer_order_counts.values() if v > 1)
    repeat_rate = round((repeat / len(customer_order_counts) * 100), 1) if customer_order_counts else 0

    # orders by status
    statuses = ["pending", "paid", "fulfilled", "shipped", "delivered", "cancelled"]
    orders_by_status = {}
    for s in statuses:
        orders_by_status[s] = await orders.count_documents({"status": s})

    # low stock products
    low_stock = await products.find({"stock": {"$lt": 10}, "status": "active"}, {"_id": 0}).sort("stock", 1).limit(10).to_list(10)
    out_of_stock = await products.count_documents({"stock": 0, "status": "active"})

    # top products (by bestseller flag as proxy + review count)
    top_products = await products.find({"status": "active"}, {"_id": 0}).sort([("bestseller", -1), ("review_count", -1)]).limit(8).to_list(8)

    # meal collection performance (placeholder counts)
    meal_perf = []
    async for mc in meal_collections.find({}, {"_id": 0}):
        meal_perf.append({
            "title": mc["title"], "slug": mc["slug"], "meal_tag": mc["meal_tag"],
            "orders_linked": sum(1 for o in paid_month if any(mc["meal_tag"] in (it.get("name", "").lower()) for it in o.get("items", [])))
        })

    # abandoned carts (no associated paid order, >1h old, has items)
    abandoned = await carts.count_documents({"items": {"$not": {"$size": 0}}})

    # AI sessions today
    ai_today = await ai_sessions.count_documents({"updated_at": {"$gte": today_iso}})

    # Recent orders
    recent = await orders.find({}, {"_id": 0}).sort("created_at", -1).limit(8).to_list(8)

    return {
        "sales": {"today": round(sum_today, 2), "week": round(sum_week, 2), "month": round(sum_month, 2)},
        "aov": aov,
        "repeat_purchase_rate": repeat_rate,
        "orders_by_status": orders_by_status,
        "low_stock_products": low_stock,
        "out_of_stock_count": out_of_stock,
        "top_products": top_products,
        "meal_performance": meal_perf,
        "abandoned_carts": abandoned,
        "ai_sessions_today": ai_today,
        "recent_orders": recent,
        "totals": {
            "products": await products.count_documents({}),
            "customers": await customers.count_documents({}),
            "orders": await orders.count_documents({}),
            "categories": await categories.count_documents({}),
        },
    }


# --- Product CRUD ---
@router.get("/products")
async def admin_list_products(q: Optional[str] = None, status: Optional[str] = None,
                               category: Optional[str] = None, limit: int = 100, skip: int = 0,
                               payload=Depends(require_admin)):
    query = {}
    if q:
        query["$or"] = [{"name": {"$regex": q, "$options": "i"}}, {"sku": {"$regex": q, "$options": "i"}}]
    if status:
        query["status"] = status
    if category:
        cat = await categories.find_one({"slug": category}, {"_id": 0})
        if cat:
            query["category_id"] = cat["id"]
    total = await products.count_documents(query)
    items = await products.find(query, {"_id": 0}).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": items, "total": total}


@router.get("/products/{product_id}")
async def admin_get_product(product_id: str, payload=Depends(require_admin)):
    p = await products.find_one({"id": product_id}, {"_id": 0})
    if not p:
        raise HTTPException(404)
    return p


@router.post("/products")
async def admin_create_product(data: Dict[str, Any], payload=Depends(require_admin)):
    doc = {
        "id": new_id(),
        "name": data.get("name", "Untitled Product"),
        "slug": data.get("slug", new_id()[:8]),
        "brand": data.get("brand", "Afrobean"),
        "description": data.get("description", ""),
        "category_id": data.get("category_id"),
        "subcategory_id": None,
        "images": data.get("images", []),
        "tags": data.get("tags", []), "cuisine_tags": data.get("cuisine_tags", []),
        "meal_tags": data.get("meal_tags", []), "dietary_tags": [],
        "use_case_tags": [], "collection_tags": [],
        "ai_meal_roles": data.get("ai_meal_roles", []),
        "variants": data.get("variants", []),
        "price": float(data.get("price", 0)),
        "compare_at_price": data.get("compare_at_price"),
        "cost_price": data.get("cost_price"),
        "sku": data.get("sku", f"AFB-{new_id()[:8].upper()}"),
        "barcode": data.get("barcode", ""),
        "stock": int(data.get("stock", 0)),
        "low_stock_threshold": int(data.get("low_stock_threshold", 5)),
        "reorder_threshold": int(data.get("reorder_threshold", 10)),
        "related_product_ids": [], "upsell_product_ids": [], "substitute_product_ids": [],
        "featured": bool(data.get("featured", False)),
        "bestseller": bool(data.get("bestseller", False)),
        "new_arrival": bool(data.get("new_arrival", False)),
        "bundle_eligible": True,
        "status": data.get("status", "draft"),
        "avg_rating": 0, "review_count": 0,
        "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
    }
    await products.insert_one(doc)
    await log_audit(payload, "product.create", "product", doc["id"], {"name": doc["name"]})
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/products/{product_id}")
async def admin_update_product(product_id: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data["updated_at"] = utcnow_iso()
    data.pop("id", None)
    await products.update_one({"id": product_id}, {"$set": data})
    await log_audit(payload, "product.update", "product", product_id, data)
    return await products.find_one({"id": product_id}, {"_id": 0})


@router.delete("/products/{product_id}")
async def admin_archive_product(product_id: str, payload=Depends(require_admin)):
    await products.update_one({"id": product_id}, {"$set": {"status": "archived", "updated_at": utcnow_iso()}})
    await log_audit(payload, "product.archive", "product", product_id)
    return {"ok": True}


@router.post("/products/bulk")
async def admin_bulk_products(data: Dict[str, Any], payload=Depends(require_admin)):
    """Bulk action: update status / stock / tags. data = {ids: [...], action: 'publish'|'archive'|'stock'|'tag', value: any}"""
    ids = data.get("ids", [])
    action = data.get("action")
    value = data.get("value")
    update = {"updated_at": utcnow_iso()}
    if action == "publish":
        update["status"] = "active"
    elif action == "archive":
        update["status"] = "archived"
    elif action == "draft":
        update["status"] = "draft"
    elif action == "stock":
        update["stock"] = int(value or 0)
    elif action == "price":
        update["price"] = float(value or 0)
    elif action == "tag":
        # push tag
        await products.update_many({"id": {"$in": ids}}, {"$addToSet": {"tags": value}})
        await log_audit(payload, "product.bulk_tag", "product", ids, {"tag": value})
        return {"ok": True, "count": len(ids)}
    result = await products.update_many({"id": {"$in": ids}}, {"$set": update})
    await log_audit(payload, f"product.bulk_{action}", "product", ids, update)
    return {"ok": True, "count": result.modified_count}


# --- Categories CRUD ---
@router.get("/categories")
async def admin_list_categories(payload=Depends(require_admin)):
    docs = await categories.find({}, {"_id": 0}).sort("sort_order", 1).to_list(200)
    for c in docs:
        c["product_count"] = await products.count_documents({"category_id": c["id"]})
    return docs


@router.post("/categories")
async def admin_create_category(data: Dict[str, Any], payload=Depends(require_admin)):
    doc = {
        "id": new_id(), "name": data["name"], "slug": data["slug"],
        "description": data.get("description", ""), "image": data.get("image", ""),
        "sort_order": int(data.get("sort_order", 0)), "visible": bool(data.get("visible", True)),
        "seo_title": data.get("seo_title", ""), "seo_description": data.get("seo_description", ""),
        "parent_id": data.get("parent_id"), "created_at": utcnow_iso(),
    }
    await categories.insert_one(doc)
    await log_audit(payload, "category.create", "category", doc["id"])
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/categories/{cat_id}")
async def admin_update_category(cat_id: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await categories.update_one({"id": cat_id}, {"$set": data})
    await log_audit(payload, "category.update", "category", cat_id)
    return await categories.find_one({"id": cat_id}, {"_id": 0})


@router.delete("/categories/{cat_id}")
async def admin_delete_category(cat_id: str, payload=Depends(require_admin)):
    await categories.delete_one({"id": cat_id})
    await log_audit(payload, "category.delete", "category", cat_id)
    return {"ok": True}


# --- Collections CRUD ---
@router.get("/collections")
async def admin_list_collections(payload=Depends(require_admin)):
    docs = await collections_col.find({}, {"_id": 0}).sort("sort_order", 1).to_list(200)
    return docs


@router.post("/collections")
async def admin_create_collection(data: Dict[str, Any], payload=Depends(require_admin)):
    doc = {
        "id": new_id(), "title": data["title"], "slug": data["slug"],
        "description": data.get("description", ""), "image": data.get("image", ""),
        "type": data.get("type", "manual"), "product_ids": data.get("product_ids", []),
        "rules": data.get("rules"), "visible": True, "sort_order": int(data.get("sort_order", 0)),
        "created_at": utcnow_iso(),
    }
    await collections_col.insert_one(doc)
    await log_audit(payload, "collection.create", "collection", doc["id"])
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/collections/{col_id}")
async def admin_update_collection(col_id: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await collections_col.update_one({"id": col_id}, {"$set": data})
    await log_audit(payload, "collection.update", "collection", col_id)
    return await collections_col.find_one({"id": col_id}, {"_id": 0})


@router.delete("/collections/{col_id}")
async def admin_delete_collection(col_id: str, payload=Depends(require_admin)):
    await collections_col.delete_one({"id": col_id})
    await log_audit(payload, "collection.delete", "collection", col_id)
    return {"ok": True}


# --- Meal collections + AI mapping ---
@router.get("/meal-collections")
async def admin_meal_collections(payload=Depends(require_admin)):
    docs = await meal_collections.find({}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    return docs


@router.get("/meal-collections/{mc_id}")
async def admin_meal_collection(mc_id: str, payload=Depends(require_admin)):
    m = await meal_collections.find_one({"id": mc_id}, {"_id": 0})
    if not m:
        raise HTTPException(404)
    return m


@router.patch("/meal-collections/{mc_id}")
async def admin_update_meal_collection(mc_id: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await meal_collections.update_one({"id": mc_id}, {"$set": data})
    await log_audit(payload, "meal_collection.update", "meal_collection", mc_id, {"keys": list(data.keys())})
    return await meal_collections.find_one({"id": mc_id}, {"_id": 0})


@router.post("/meal-collections/{mc_id}/preview-basket")
async def preview_meal_basket(mc_id: str, data: Dict[str, Any], payload=Depends(require_admin)):
    """Preview what the AI would assemble."""
    m = await meal_collections.find_one({"id": mc_id}, {"_id": 0})
    if not m:
        raise HTTPException(404)
    basket = []
    for slot in m.get("required_slots", []):
        if slot.get("default_product_ids"):
            p = await products.find_one({"id": slot["default_product_ids"][0]}, {"_id": 0})
            if p:
                basket.append({"slot": slot["slot_key"], "product": p, "quantity": 1, "required": True})
    for slot in m.get("optional_slots", []):
        if slot.get("default_product_ids"):
            p = await products.find_one({"id": slot["default_product_ids"][0]}, {"_id": 0})
            if p:
                basket.append({"slot": slot["slot_key"], "product": p, "quantity": 1, "required": False})
    total = sum(i["product"]["price"] * i["quantity"] for i in basket)
    return {"basket": basket, "total": round(total, 2)}


# --- Bundles ---
@router.get("/bundles")
async def admin_bundles(payload=Depends(require_admin)):
    docs = await bundles.find({}, {"_id": 0}).to_list(100)
    return docs


@router.post("/bundles")
async def admin_create_bundle(data: Dict[str, Any], payload=Depends(require_admin)):
    doc = {
        "id": new_id(), "title": data["title"], "slug": data["slug"],
        "description": data.get("description", ""), "image": data.get("image", ""),
        "items": data.get("items", []), "optional_items": data.get("optional_items", []),
        "price": float(data.get("price", 0)), "compare_at_price": data.get("compare_at_price"),
        "discount_type": data.get("discount_type", "fixed"), "tier": data.get("tier", "standard"),
        "meal_tag": data.get("meal_tag"), "active": True, "created_at": utcnow_iso(),
    }
    await bundles.insert_one(doc)
    await log_audit(payload, "bundle.create", "bundle", doc["id"])
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/bundles/{bid}")
async def admin_update_bundle(bid: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await bundles.update_one({"id": bid}, {"$set": data})
    await log_audit(payload, "bundle.update", "bundle", bid)
    return await bundles.find_one({"id": bid}, {"_id": 0})


@router.delete("/bundles/{bid}")
async def admin_delete_bundle(bid: str, payload=Depends(require_admin)):
    await bundles.update_one({"id": bid}, {"$set": {"active": False}})
    await log_audit(payload, "bundle.delete", "bundle", bid)
    return {"ok": True}


# --- Inventory ---
@router.get("/inventory")
async def admin_inventory(view: Optional[str] = None, payload=Depends(require_admin)):
    query = {}
    if view == "low_stock":
        query = {"stock": {"$lt": 10, "$gt": 0}}
    elif view == "out_of_stock":
        query = {"stock": 0}
    elif view == "fast_movers":
        query = {"bestseller": True}
    elif view == "dead_stock":
        query = {"bestseller": False, "stock": {"$gt": 50}}
    docs = await products.find(query, {"_id": 0}).sort("stock", 1).limit(200).to_list(200)
    return docs


@router.post("/inventory/adjust")
async def admin_adjust_stock(data: Dict[str, Any], payload=Depends(require_admin)):
    pid = data["product_id"]
    delta = int(data.get("delta", 0))
    reason = data.get("reason", "adjustment")
    p = await products.find_one({"id": pid}, {"_id": 0})
    if not p:
        raise HTTPException(404)
    new_stock = max(0, p["stock"] + delta)
    await products.update_one({"id": pid}, {"$set": {"stock": new_stock, "updated_at": utcnow_iso()}})
    await log_audit(payload, "inventory.adjust", "product", pid, {"delta": delta, "reason": reason, "new_stock": new_stock})
    return {"ok": True, "stock": new_stock}


# --- Orders (admin) ---
@router.get("/orders")
async def admin_orders(status: Optional[str] = None, q: Optional[str] = None,
                       limit: int = 100, skip: int = 0, payload=Depends(require_admin)):
    query = {}
    if status:
        query["status"] = status
    if q:
        query["$or"] = [{"order_number": {"$regex": q, "$options": "i"}},
                        {"customer_email": {"$regex": q, "$options": "i"}}]
    total = await orders.count_documents(query)
    items = await orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": items, "total": total}


@router.get("/orders/{order_number}")
async def admin_order(order_number: str, payload=Depends(require_admin)):
    o = await orders.find_one({"order_number": order_number}, {"_id": 0})
    if not o:
        raise HTTPException(404)
    return o


@router.patch("/orders/{order_number}")
async def admin_update_order(order_number: str, data: Dict[str, Any], payload=Depends(require_admin)):
    update = {"updated_at": utcnow_iso()}
    for k in ["status", "fulfillment_status", "delivery_status", "notes"]:
        if k in data:
            update[k] = data[k]
    # Add timeline entry
    timeline_entry = {"at": utcnow_iso(), "by": payload.get("email"), "change": update}
    await orders.update_one({"order_number": order_number},
                            {"$set": update, "$push": {"timeline": timeline_entry}})
    await log_audit(payload, "order.update", "order", order_number, update)
    return await orders.find_one({"order_number": order_number}, {"_id": 0})


# --- Customers ---
@router.get("/customers")
async def admin_customers(q: Optional[str] = None, limit: int = 100, skip: int = 0, payload=Depends(require_admin)):
    query = {}
    if q:
        query["$or"] = [{"email": {"$regex": q, "$options": "i"}}, {"name": {"$regex": q, "$options": "i"}}]
    total = await customers.count_documents(query)
    items = await customers.find(query, {"_id": 0, "password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": items, "total": total}


@router.get("/customers/{cid}")
async def admin_customer(cid: str, payload=Depends(require_admin)):
    c = await customers.find_one({"id": cid}, {"_id": 0, "password_hash": 0})
    if not c:
        raise HTTPException(404)
    c["orders"] = await orders.find({"customer_id": cid}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)
    return c


# --- Messaging & Automations ---
@router.get("/messaging/templates")
async def list_templates(payload=Depends(require_admin)):
    return await message_templates.find({}, {"_id": 0}).to_list(100)


@router.post("/messaging/templates")
async def create_template(data: Dict[str, Any], payload=Depends(require_admin)):
    doc = {"id": new_id(), **data, "active": True, "created_at": utcnow_iso()}
    await message_templates.insert_one(doc)
    await log_audit(payload, "template.create", "template", doc["id"])
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/messaging/templates/{tid}")
async def update_template(tid: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await message_templates.update_one({"id": tid}, {"$set": data})
    await log_audit(payload, "template.update", "template", tid)
    return await message_templates.find_one({"id": tid}, {"_id": 0})


@router.get("/messaging/automations")
async def list_automations(payload=Depends(require_admin)):
    return await automation_flows.find({}, {"_id": 0}).to_list(100)


@router.patch("/messaging/automations/{aid}")
async def update_automation(aid: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await automation_flows.update_one({"id": aid}, {"$set": data})
    await log_audit(payload, "automation.update", "automation", aid)
    return await automation_flows.find_one({"id": aid}, {"_id": 0})


# --- Analytics ---
@router.get("/analytics/overview")
async def analytics_overview(payload=Depends(require_admin)):
    now = datetime.now(timezone.utc)
    month_ago = (now - timedelta(days=30)).isoformat()
    paid = await orders.find({"payment_status": "paid", "created_at": {"$gte": month_ago}}, {"_id": 0}).to_list(5000)

    # Sales by category
    cat_docs = await categories.find({}, {"_id": 0}).to_list(100)
    cat_map = {c["id"]: c["name"] for c in cat_docs}
    by_category = {}
    # Need to look up each product's category
    prod_cache = {}
    for o in paid:
        for it in o.get("items", []):
            pid = it["product_id"]
            if pid not in prod_cache:
                p = await products.find_one({"id": pid}, {"_id": 0, "category_id": 1})
                prod_cache[pid] = p.get("category_id") if p else None
            catname = cat_map.get(prod_cache[pid], "Other")
            by_category[catname] = by_category.get(catname, 0) + it["price"] * it["quantity"]

    by_category_arr = sorted([{"name": k, "value": round(v, 2)} for k, v in by_category.items()], key=lambda x: -x["value"])

    top_products = await products.find({}, {"_id": 0, "name": 1, "slug": 1, "avg_rating": 1, "review_count": 1, "price": 1, "images": 1, "bestseller": 1}).sort([("bestseller", -1), ("review_count", -1)]).limit(10).to_list(10)

    return {
        "by_category": by_category_arr,
        "top_products": top_products,
        "total_revenue_30d": round(sum(o["total"] for o in paid), 2),
        "order_count_30d": len(paid),
    }


# --- Audit logs ---
@router.get("/audit-logs")
async def admin_audit_logs(limit: int = 100, payload=Depends(require_admin)):
    docs = await audit_logs.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return docs


# --- Delivery zones ---
@router.get("/delivery-zones")
async def admin_delivery_zones(payload=Depends(require_admin)):
    return await delivery_zones.find({}, {"_id": 0}).to_list(10)


@router.patch("/delivery-zones/{zid}")
async def admin_update_delivery_zone(zid: str, data: Dict[str, Any], payload=Depends(require_admin)):
    data.pop("id", None)
    await delivery_zones.update_one({"id": zid}, {"$set": data})
    await log_audit(payload, "delivery_zone.update", "delivery_zone", zid)
    return await delivery_zones.find_one({"id": zid}, {"_id": 0})


# --- Imports (CSV) ---
@router.post("/imports/products")
async def import_products(file: UploadFile = File(...), payload=Depends(require_admin)):
    text = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))
    created, errors = 0, []
    for row in reader:
        try:
            if not row.get("name") or not row.get("slug"):
                errors.append({"row": row, "error": "missing name/slug"})
                continue
            price = float(row.get("price", 0))
            doc = {
                "id": new_id(),
                "name": row["name"], "slug": row["slug"],
                "brand": row.get("brand", "Afrobean"),
                "description": row.get("description", ""),
                "category_id": None,
                "subcategory_id": None,
                "images": [row["image"]] if row.get("image") else [],
                "tags": [t.strip() for t in row.get("tags", "").split(",") if t.strip()],
                "cuisine_tags": [], "meal_tags": [t.strip() for t in row.get("meal_tags", "").split(",") if t.strip()],
                "dietary_tags": [], "use_case_tags": [], "collection_tags": [],
                "ai_meal_roles": [r.strip() for r in row.get("ai_meal_roles", "").split(",") if r.strip()],
                "variants": [{"size_label": row.get("size_label", "Standard"), "pack_class": "single",
                              "price": price, "compare_at_price": None,
                              "sku": row.get("sku", f"AFB-{new_id()[:8].upper()}"),
                              "stock": int(row.get("stock", 0)), "is_default": True, "is_best_value": False}],
                "price": price, "compare_at_price": None, "cost_price": None,
                "sku": row.get("sku", f"AFB-{new_id()[:8].upper()}"), "barcode": "",
                "stock": int(row.get("stock", 0)), "low_stock_threshold": 5, "reorder_threshold": 10,
                "related_product_ids": [], "upsell_product_ids": [], "substitute_product_ids": [],
                "featured": row.get("featured", "").lower() == "true",
                "bestseller": row.get("bestseller", "").lower() == "true",
                "new_arrival": False, "bundle_eligible": True,
                "status": row.get("status", "draft"),
                "avg_rating": 0, "review_count": 0,
                "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
            }
            # Resolve category_slug to id
            if row.get("category_slug"):
                cat = await categories.find_one({"slug": row["category_slug"]}, {"_id": 0})
                if cat:
                    doc["category_id"] = cat["id"]
            await products.insert_one(doc)
            created += 1
        except Exception as e:
            errors.append({"row": row, "error": str(e)})
    await imports.insert_one({"id": new_id(), "type": "products", "created": created,
                              "errors": errors, "actor": payload.get("email"), "created_at": utcnow_iso()})
    await log_audit(payload, "import.products", "import", None, {"created": created, "errors": len(errors)})
    return {"created": created, "errors": errors}


@router.get("/imports")
async def list_imports(payload=Depends(require_admin)):
    return await imports.find({}, {"_id": 0}).sort("created_at", -1).limit(50).to_list(50)


# --- Export CSV ---
@router.get("/exports/products")
async def export_products(payload=Depends(require_admin)):
    from fastapi.responses import StreamingResponse
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["name", "slug", "brand", "description", "category_slug",
                     "price", "compare_at_price", "cost_price", "sku", "stock",
                     "featured", "bestseller", "meal_tags", "tags", "status", "image"])
    cat_map = {}
    async for c in categories.find({}, {"_id": 0}):
        cat_map[c["id"]] = c["slug"]
    async for p in products.find({}, {"_id": 0}):
        writer.writerow([
            p["name"], p["slug"], p.get("brand", ""), p.get("description", "")[:200],
            cat_map.get(p.get("category_id"), ""),
            p["price"], p.get("compare_at_price") or "", p.get("cost_price") or "",
            p.get("sku", ""), p.get("stock", 0),
            p.get("featured", False), p.get("bestseller", False),
            ",".join(p.get("meal_tags", [])), ",".join(p.get("tags", [])),
            p.get("status", ""), p["images"][0] if p.get("images") else "",
        ])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=afrobean-products.csv"})


# --- Settings / roles ---
@router.get("/admin-users")
async def admin_list_admin_users(payload=Depends(require_admin)):
    return await admin_users.find({}, {"_id": 0, "password_hash": 0}).to_list(100)


@router.post("/admin-users")
async def admin_create_admin_user(data: Dict[str, Any], payload=Depends(require_admin)):
    if payload.get("role") != "super_admin":
        raise HTTPException(403, "Super admin only")
    if await admin_users.find_one({"email": data["email"]}):
        raise HTTPException(400, "Email exists")
    doc = {
        "id": new_id(), "email": data["email"], "name": data.get("name", ""),
        "role": data.get("role", "operations"),
        "password_hash": hash_password(data["password"]),
        "active": True, "created_at": utcnow_iso(),
    }
    await admin_users.insert_one(doc)
    await log_audit(payload, "admin_user.create", "admin_user", doc["id"], {"role": doc["role"]})
    return {k: v for k, v in doc.items() if k != "password_hash"}


@router.patch("/admin-users/{uid}")
async def admin_update_admin_user(uid: str, data: Dict[str, Any], payload=Depends(require_admin)):
    if payload.get("role") != "super_admin":
        raise HTTPException(403, "Super admin only")
    data.pop("id", None)
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))
    await admin_users.update_one({"id": uid}, {"$set": data})
    await log_audit(payload, "admin_user.update", "admin_user", uid)
    return await admin_users.find_one({"id": uid}, {"_id": 0, "password_hash": 0})
