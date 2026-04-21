"""Catalogue routes: categories, products, collections, meal collections, bundles, reviews."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from db import (
    products, categories, collections_col, meal_collections, bundles, reviews, clean
)
from models import utcnow_iso

router = APIRouter(prefix="/api")


# --- Categories ---
@router.get("/categories")
async def list_categories():
    docs = await categories.find({"visible": True}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    # attach product count
    out = []
    for c in docs:
        c["product_count"] = await products.count_documents({"category_id": c["id"], "status": "active"})
        out.append(c)
    return out


@router.get("/categories/{slug}")
async def get_category(slug: str):
    cat = await categories.find_one({"slug": slug}, {"_id": 0})
    if not cat:
        raise HTTPException(404, "Category not found")
    prods = await products.find(
        {"category_id": cat["id"], "status": "active"}, {"_id": 0}
    ).sort("bestseller", -1).to_list(200)
    return {"category": cat, "products": prods}


# --- Products ---
@router.get("/products")
async def list_products(
    q: Optional[str] = None,
    category: Optional[str] = None,
    meal: Optional[str] = None,
    collection: Optional[str] = None,
    bestseller: Optional[bool] = None,
    featured: Optional[bool] = None,
    new_arrival: Optional[bool] = None,
    sort: Optional[str] = "bestseller",
    limit: int = 60,
    skip: int = 0,
):
    query = {"status": "active"}
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
            {"brand": {"$regex": q, "$options": "i"}},
        ]
    if category:
        cat = await categories.find_one({"slug": category}, {"_id": 0})
        if cat:
            query["category_id"] = cat["id"]
    if meal:
        query["meal_tags"] = meal
    if bestseller:
        query["bestseller"] = True
    if featured:
        query["featured"] = True
    if new_arrival:
        query["new_arrival"] = True

    sort_map = {
        "price_asc": [("price", 1)], "price_desc": [("price", -1)],
        "newest": [("created_at", -1)], "bestseller": [("bestseller", -1), ("avg_rating", -1)],
        "name": [("name", 1)],
    }
    cursor = products.find(query, {"_id": 0}).sort(sort_map.get(sort, sort_map["bestseller"])).skip(skip).limit(limit)
    docs = await cursor.to_list(limit)
    total = await products.count_documents(query)
    return {"items": docs, "total": total}


@router.get("/products/{slug}")
async def get_product(slug: str):
    p = await products.find_one({"slug": slug, "status": "active"}, {"_id": 0})
    if not p:
        raise HTTPException(404, "Product not found")
    # related & reviews
    related_q = {"status": "active", "id": {"$ne": p["id"]}}
    if p.get("meal_tags"):
        related_q["meal_tags"] = {"$in": p["meal_tags"]}
    related = await products.find(related_q, {"_id": 0}).limit(8).to_list(8)
    revs = await reviews.find({"product_id": p["id"]}, {"_id": 0}).sort("created_at", -1).limit(12).to_list(12)
    cat = await categories.find_one({"id": p["category_id"]}, {"_id": 0})
    return {"product": p, "related": related, "reviews": revs, "category": cat}


# --- Collections ---
@router.get("/collections")
async def list_collections():
    docs = await collections_col.find({"visible": True}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    return docs


@router.get("/collections/{slug}")
async def get_collection(slug: str):
    c = await collections_col.find_one({"slug": slug}, {"_id": 0})
    if not c:
        raise HTTPException(404, "Collection not found")
    # smart collections
    if c["type"] == "smart" and c["slug"] == "best-sellers":
        prods = await products.find({"bestseller": True, "status": "active"}, {"_id": 0}).limit(60).to_list(60)
    elif c["type"] == "smart" and c["slug"] == "new-arrivals":
        prods = await products.find({"new_arrival": True, "status": "active"}, {"_id": 0}).limit(60).to_list(60)
    elif c.get("product_ids"):
        prods = await products.find({"id": {"$in": c["product_ids"]}, "status": "active"}, {"_id": 0}).to_list(60)
    else:
        # For manual collections without explicit IDs, show featured
        prods = await products.find({"featured": True, "status": "active"}, {"_id": 0}).limit(20).to_list(20)
    return {"collection": c, "products": prods}


# --- Meal Collections ---
@router.get("/meal-collections")
async def list_meal_collections():
    docs = await meal_collections.find({"visible": True}, {"_id": 0}).sort("sort_order", 1).to_list(100)
    return docs


@router.get("/meal-collections/{slug}")
async def get_meal_collection(slug: str):
    m = await meal_collections.find_one({"slug": slug, "active": True}, {"_id": 0})
    if not m:
        raise HTTPException(404, "Meal collection not found")
    # Hydrate slots with product details
    all_pids = set()
    for slot in m.get("required_slots", []) + m.get("optional_slots", []):
        all_pids.update(slot.get("default_product_ids", []))
        all_pids.update(slot.get("substitute_product_ids", []))
    all_pids.update(m.get("protein_options", []))
    all_pids.update(m.get("upsell_product_ids", []))
    prod_list = await products.find({"id": {"$in": list(all_pids)}, "status": "active"}, {"_id": 0}).to_list(200)
    prod_map = {p["id"]: p for p in prod_list}
    return {"meal_collection": m, "products": list(prod_map.values()), "product_map_keys": list(prod_map.keys())}


# --- Bundles ---
@router.get("/bundles")
async def list_bundles():
    docs = await bundles.find({"active": True}, {"_id": 0}).to_list(100)
    return docs


@router.get("/bundles/{slug}")
async def get_bundle(slug: str):
    b = await bundles.find_one({"slug": slug, "active": True}, {"_id": 0})
    if not b:
        raise HTTPException(404, "Bundle not found")
    pids = [i["product_id"] for i in b.get("items", [])]
    prod_list = await products.find({"id": {"$in": pids}}, {"_id": 0}).to_list(100)
    return {"bundle": b, "products": prod_list}


# --- Reviews ---
@router.get("/reviews")
async def list_reviews(product_slug: Optional[str] = None, limit: int = 12):
    query = {}
    if product_slug:
        p = await products.find_one({"slug": product_slug}, {"_id": 0, "id": 1})
        if p:
            query["product_id"] = p["id"]
    revs = await reviews.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return revs
