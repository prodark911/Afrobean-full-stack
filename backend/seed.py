"""Seed data for Afrobean — uses real catalog from catalog_data.json + real HQ product images."""
import os, json, random
from datetime import datetime, timezone
from auth import hash_password
from db import (
    admin_users, customers, categories, products, collections_col,
    meal_collections, bundles, message_templates, automation_flows,
    delivery_zones, reviews, audit_logs,
)
from models import utcnow_iso, new_id

random.seed(42)

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog_data.json")


CATEGORIES = [
    {"name": "Rice, Flour & Swallows", "slug": "rice-flour-swallows", "sort_order": 1,
     "description": "Staple rice, flours, semovita, poundo, garri, and all your swallow essentials."},
    {"name": "Beans, Grains & Nuts", "slug": "beans-grains-nuts", "sort_order": 2,
     "description": "Brown beans, black-eyed peas, groundnuts, hominy, hibiscus and more."},
    {"name": "Oils & Cooking Essentials", "slug": "oils-cooking-essentials", "sort_order": 3,
     "description": "Palm oil, groundnut oil, vegetable oil, and cooking basics."},
    {"name": "Spices & Seasonings", "slug": "spices-seasonings", "sort_order": 4,
     "description": "Authentic African spices, stock cubes, curry, thyme, ehuru, uziza."},
    {"name": "Sauces, Pastes & Soup Bases", "slug": "sauces-pastes-soup-bases", "sort_order": 5,
     "description": "Tomato pastes, banga base, shito, egusi, ayamase and more."},
    {"name": "Breakfast & Cereals", "slug": "breakfast-cereals", "sort_order": 6,
     "description": "Oats, pap, custard, milk powder, Milo, Bournvita and cornflakes."},
    {"name": "Drinks & Teas", "slug": "drinks-teas", "sort_order": 7,
     "description": "Malt drinks, ginger tea, hibiscus (zobo) and sparkling non-alcoholics."},
    {"name": "Snacks & Biscuits", "slug": "snacks-biscuits", "sort_order": 8,
     "description": "Chin chin, plantain chips, kulikuli, kokoro, biscuits and more."},
    {"name": "Canned Foods", "slug": "canned-foods", "sort_order": 9,
     "description": "Canned sardines, corned beef, Vienna sausages and tinned vegetables."},
    {"name": "Frozen Fish & Meat", "slug": "frozen-fish-meat", "sort_order": 10,
     "description": "Frozen croaker, tilapia, hake, mackerel, goat meat and poultry."},
    {"name": "Beauty & Personal Care", "slug": "beauty-personal-care", "sort_order": 11,
     "description": "Shea butter, black soap and natural personal care."},
    {"name": "Household Essentials", "slug": "household-essentials", "sort_order": 12,
     "description": "Kitchen and cleaning essentials for your home."},
]

CAT_IMG = {
    "rice-flour-swallows": "/products/image10.webp",
    "beans-grains-nuts": "/products/image73.webp",
    "oils-cooking-essentials": "/products/image51.webp",
    "spices-seasonings": "/products/image197.webp",
    "sauces-pastes-soup-bases": "/products/image317.webp",
    "breakfast-cereals": "/products/image235.webp",
    "drinks-teas": "/products/image263.webp",
    "snacks-biscuits": "/products/image261.webp",
    "canned-foods": "/products/image232.webp",
    "frozen-fish-meat": "/products/image1.webp",  # fallback
    "beauty-personal-care": "/products/image5.webp",
    "household-essentials": "/products/image201.webp",
}


MEAL_COLLECTIONS = [
    {"title": "Jollof Rice Essentials", "slug": "jollof-rice-essentials", "meal_tag": "jollof",
     "description": "Everything you need for a pot of party-perfect Jollof rice.",
     "hero_image": "/products/image41.webp",
     "user_intent_phrases": ["jollof rice", "make jollof", "cook jollof", "party jollof", "nigerian jollof"],
     "required_slot_keys": [("rice_base","Long grain rice"),("tomato_base","Tomato paste / base"),
                            ("jollof_seasoning","Jollof spice mix"),("curry","Curry powder"),
                            ("thyme","Thyme"),("oil","Cooking oil"),("stock_seasoning","Stock seasoning")],
     "optional_slot_keys": [("protein","Choose your protein")], "servings_default": 5},
    {"title": "Pepper Soup Essentials", "slug": "pepper-soup-essentials", "meal_tag": "pepper_soup",
     "description": "Spicy, aromatic pepper soup — the full ingredient list.",
     "hero_image": "/products/image228.webp",
     "user_intent_phrases": ["pepper soup","ngwo-ngwo","peppersoup","catfish pepper soup"],
     "required_slot_keys": [("pepper_soup_spice","Pepper soup spice"),("stock_seasoning","Stock seasoning"),("protein","Protein (fish/meat)")],
     "optional_slot_keys": [("ehuru","Ehuru (calabash nutmeg)"),("uziza","Uziza seeds"),("swallow","Swallow of choice")],
     "servings_default": 4},
    {"title": "Moi Moi Essentials", "slug": "moi-moi-essentials", "meal_tag": "moi_moi",
     "description": "Steamed bean pudding — everything from beans to pouches.",
     "hero_image": "/products/image70.webp",
     "user_intent_phrases": ["moi moi","moin moin","bean pudding"],
     "required_slot_keys": [("beans","Peeled beans"),("oil","Palm oil"),("stock_seasoning","Seasoning"),("moi_moi_pouch","Cooking pouches")],
     "optional_slot_keys": [("protein","Fish / egg"),("crayfish","Ground crayfish")],
     "servings_default": 6},
    {"title": "Banga Soup Essentials", "slug": "banga-soup-essentials", "meal_tag": "banga",
     "description": "Rich palm-fruit soup, perfect with starch or eba.",
     "hero_image": "/products/image313.webp",
     "user_intent_phrases": ["banga","banga soup","ofe akwu","palm nut soup"],
     "required_slot_keys": [("banga_base","Palm-fruit base"),("banga_spice","Banga spice"),("stock_seasoning","Seasoning"),("protein","Protein")],
     "optional_slot_keys": [("swallow","Swallow of choice"),("crayfish","Ground crayfish")],
     "servings_default": 4},
    {"title": "Efo Riro Essentials", "slug": "efo-riro-essentials", "meal_tag": "efo_riro",
     "description": "Rich Yoruba spinach stew with everything you need.",
     "hero_image": "/products/image325.webp" if False else "/products/image32.webp",
     "user_intent_phrases": ["efo riro","vegetable soup","efo"],
     "required_slot_keys": [("efo_leaves","Leaf spinach"),("tomato_base","Tomato base"),("palm_oil","Palm oil"),("stock_seasoning","Seasoning"),("protein","Protein")],
     "optional_slot_keys": [("iru","Locust beans (iru)"),("crayfish","Ground crayfish")],
     "servings_default": 4},
    {"title": "Breakfast Staples", "slug": "breakfast-staples", "meal_tag": "breakfast",
     "description": "Everything for a week of beautiful African breakfasts.",
     "hero_image": "/products/image235.webp",
     "user_intent_phrases": ["breakfast","pap","custard","oats","milo"],
     "required_slot_keys": [("oats","Oats"),("pap","Pap / ogi"),("custard","Custard"),("milk","Milk powder"),("cocoa","Cocoa beverage")],
     "optional_slot_keys": [("cereal","Cornflakes")],
     "servings_default": 4},
]


BUNDLES = [
    {"title": "Jollof Rice Combo", "slug": "jollof-rice-combo", "meal_tag": "jollof",
     "description": "Everything you need for 5 servings of Jollof rice.",
     "image": "/products/image41.webp", "price": 29.99, "compare_at_price": 35.50, "tier": "standard"},
    {"title": "Pepper Soup Combo", "slug": "pepper-soup-combo", "meal_tag": "pepper_soup",
     "description": "Pepper soup spices + protein bundle.",
     "image": "/products/image228.webp", "price": 24.99, "compare_at_price": 29.50, "tier": "standard"},
    {"title": "Family Swallow Bundle", "slug": "family-swallow-bundle",
     "description": "Yam flour, garri, semovita & plantain flour — family-size pack.",
     "image": "/products/image14.webp", "price": 22.99, "compare_at_price": 26.50, "tier": "family"},
    {"title": "Breakfast Combo", "slug": "breakfast-combo", "meal_tag": "breakfast",
     "description": "Oats, pap, custard, milk & Milo — a week of breakfasts.",
     "image": "/products/image235.webp", "price": 27.99, "compare_at_price": 32.00, "tier": "standard"},
    {"title": "Bulk Oil Bundle", "slug": "bulk-oil-bundle",
     "description": "Palm oil + groundnut oil + vegetable oil bulk pack.",
     "image": "/products/image51.webp", "price": 33.99, "compare_at_price": 39.50, "tier": "family"},
    {"title": "Student Pantry Bundle", "slug": "student-pantry-bundle",
     "description": "Starter pantry essentials for students.",
     "image": "/products/image43.webp", "price": 39.99, "compare_at_price": 47.00, "tier": "student"},
    {"title": "New Customer Starter Box", "slug": "new-customer-starter-box",
     "description": "Welcome to Afrobean — top picks across the store.",
     "image": "/products/image197.webp", "price": 49.99, "compare_at_price": 59.00, "tier": "premium"},
]

COLLECTIONS = [
    {"title": "Best Sellers", "slug": "best-sellers", "type": "smart",
     "description": "Our most-loved products in Peterborough.", "image": "/products/image41.webp"},
    {"title": "New Arrivals", "slug": "new-arrivals", "type": "smart",
     "description": "Fresh additions to the Afrobean pantry.", "image": "/products/image197.webp"},
    {"title": "Pantry Restock", "slug": "pantry-restock", "type": "manual",
     "description": "Top up on your weekly essentials.", "image": "/products/image43.webp"},
    {"title": "Family-Size Value", "slug": "family-size-value", "type": "manual",
     "description": "Family-size packs that save you money.", "image": "/products/image14.webp"},
    {"title": "Bulk Buy Picks", "slug": "bulk-buy-picks", "type": "manual",
     "description": "Big packs for bigger savings.", "image": "/products/image74.webp"},
]

MESSAGE_TEMPLATES = [
    {"channel": "email", "name": "Welcome Series", "subject": "Welcome to Afrobean!",
     "body": "Hi {name}, welcome to Afrobean — your premium African supermarket in Peterborough. Enjoy 10% off your first order with code WELCOME10."},
    {"channel": "email", "name": "Abandoned Cart", "subject": "You left something in your basket",
     "body": "Hi {name}, your Afrobean basket is waiting. Complete checkout within 24h and enjoy free delivery over £50."},
    {"channel": "email", "name": "Post-Purchase Thank You", "subject": "Thank you for your order!",
     "body": "Hi {name}, your order {order_number} is confirmed. We're packing it now."},
    {"channel": "whatsapp", "name": "Order Update WhatsApp", "subject": "",
     "body": "Hi {name}, your Afrobean order {order_number} is out for delivery."},
    {"channel": "whatsapp", "name": "Cart Recovery WhatsApp", "subject": "",
     "body": "Hi {name}, want to finish your basket? Free delivery over £50 in Peterborough."},
    {"channel": "email", "name": "Back in Stock", "subject": "Back in stock — grab it now",
     "body": "Hi {name}, {product} is back in stock. Add it to your cart before it sells out."},
    {"channel": "email", "name": "Replenishment Reminder", "subject": "Time to restock?",
     "body": "Hi {name}, it's been {days} days since your last order. Your pantry essentials are just a click away."},
    {"channel": "email", "name": "Meal Campaign — Jollof", "subject": "Cook jollof this weekend",
     "body": "Hi {name}, shop our Jollof Essentials collection and get everything in one click."},
    {"channel": "email", "name": "Review Request", "subject": "How was your order?",
     "body": "Hi {name}, we'd love your honest review on the items you got."},
]

AUTOMATIONS = [
    {"name": "Welcome new customers", "trigger": "welcome", "channel": "email", "delay_minutes": 0, "active": True},
    {"name": "Recover abandoned cart", "trigger": "abandoned_cart", "channel": "email", "delay_minutes": 60, "active": True},
    {"name": "Post-purchase thank you", "trigger": "order_placed", "channel": "email", "delay_minutes": 5, "active": True},
    {"name": "Order shipped WhatsApp", "trigger": "order_shipped", "channel": "whatsapp", "delay_minutes": 0, "active": True},
    {"name": "30-day pantry replenishment", "trigger": "replenishment", "channel": "email", "delay_minutes": 60 * 24 * 30, "active": True},
    {"name": "Back-in-stock notification", "trigger": "back_in_stock", "channel": "email", "delay_minutes": 0, "active": True},
    {"name": "Jollof weekend campaign", "trigger": "meal_campaign", "channel": "email", "delay_minutes": 0, "active": False},
    {"name": "Review request (7d post-delivery)", "trigger": "review_request", "channel": "email", "delay_minutes": 60 * 24 * 7, "active": True},
]


def _variants(price, sku):
    return [{"size_label": "Standard", "pack_class": "single", "price": float(price),
             "compare_at_price": None, "sku": sku, "stock": random.randint(20, 80),
             "is_default": True, "is_best_value": False}]


async def seed_all(force: bool = False):
    # Admin users
    if force: await admin_users.delete_many({})
    if await admin_users.count_documents({}) == 0:
        await admin_users.insert_one({
            "id": new_id(), "email": "admin@afrobean.co.uk", "name": "Afrobean Admin",
            "role": "super_admin", "password_hash": hash_password("Admin@123"),
            "active": True, "created_at": utcnow_iso(),
        })
        await admin_users.insert_one({
            "id": new_id(), "email": "merch@afrobean.co.uk", "name": "Merchandiser User",
            "role": "merchandiser", "password_hash": hash_password("Merch@123"),
            "active": True, "created_at": utcnow_iso(),
        })

    # Customers
    if force: await customers.delete_many({})
    if await customers.count_documents({}) == 0:
        await customers.insert_one({
            "id": new_id(), "email": "demo@afrobean.co.uk", "name": "Demo Shopper",
            "phone": "07700900123", "password_hash": hash_password("Demo@123"),
            "email_consent": True, "whatsapp_consent": True, "marketing_consent": True,
            "addresses": [{"line1": "45 Westgate", "city": "Peterborough", "postcode": "PE1 1PY", "country": "UK"}],
            "created_at": utcnow_iso(), "active": True, "total_spend": 0, "order_count": 0,
            "auto_replenishment": False,
        })

    # Categories
    if force: await categories.delete_many({})
    cat_map = {}
    if await categories.count_documents({}) == 0:
        for c in CATEGORIES:
            doc = {"id": new_id(), "name": c["name"], "slug": c["slug"],
                   "description": c["description"], "image": CAT_IMG.get(c["slug"], ""),
                   "sort_order": c["sort_order"], "visible": True,
                   "seo_title": c["name"], "seo_description": c["description"],
                   "parent_id": None, "created_at": utcnow_iso()}
            await categories.insert_one(doc)
            cat_map[c["slug"]] = doc["id"]
    else:
        async for c in categories.find({}, {"_id": 0}):
            cat_map[c["slug"]] = c["id"]

    # Products - load from real catalog
    prod_slug_to_id = {}
    prod_role_to_ids = {}
    prod_meal_to_ids = {}

    if force: await products.delete_many({})
    if await products.count_documents({}) == 0:
        try:
            with open(CATALOG_PATH) as f:
                catalog = json.load(f)
        except Exception:
            catalog = []

        for idx, item in enumerate(catalog):
            pid = new_id()
            price = float(item["price"])
            compare_at = round(price * random.uniform(1.1, 1.25), 2) if random.random() < 0.3 else None
            cost = round(price * 0.62, 2)
            stock = random.randint(15, 90)
            bestseller = random.random() < 0.10
            featured = random.random() < 0.08
            new_arrival = random.random() < 0.15
            img = item.get("image") or CAT_IMG.get(item["category_slug"], "/products/image1.webp")
            doc = {
                "id": pid, "name": item["name"], "slug": item["slug"], "brand": item.get("brand", "Afrobean"),
                "description": f"{item['name']} — authentic African grocery staple, delivered fresh to your door in Peterborough.",
                "category_id": cat_map.get(item["category_slug"]),
                "subcategory_id": None,
                "images": [img],
                "tags": [], "cuisine_tags": ["african", "west-african"],
                "meal_tags": item.get("meal_tags", []), "dietary_tags": [],
                "use_case_tags": [], "collection_tags": [],
                "ai_meal_roles": item.get("ai_meal_roles", []),
                "variants": _variants(price, item["sku"]),
                "price": price, "compare_at_price": compare_at, "cost_price": cost,
                "sku": item["sku"], "barcode": "",
                "stock": stock, "low_stock_threshold": 5, "reorder_threshold": 10,
                "related_product_ids": [], "upsell_product_ids": [], "substitute_product_ids": [],
                "featured": featured, "bestseller": bestseller, "new_arrival": new_arrival,
                "bundle_eligible": True, "status": "active",
                "avg_rating": round(random.uniform(4.2, 5.0), 1),
                "review_count": random.randint(8, 240) if bestseller else random.randint(3, 60),
                "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
                "replenishment_eligible": item["category_slug"] in ("rice-flour-swallows","beans-grains-nuts","oils-cooking-essentials","breakfast-cereals","household-essentials"),
            }
            await products.insert_one(doc)
            prod_slug_to_id[item["slug"]] = pid
            for r in item.get("ai_meal_roles", []):
                prod_role_to_ids.setdefault(r, []).append(pid)
            for mt in item.get("meal_tags", []):
                prod_meal_to_ids.setdefault(mt, []).append(pid)
    else:
        async for p in products.find({}, {"_id": 0}):
            prod_slug_to_id[p["slug"]] = p["id"]
            for r in p.get("ai_meal_roles", []):
                prod_role_to_ids.setdefault(r, []).append(p["id"])
            for mt in p.get("meal_tags", []):
                prod_meal_to_ids.setdefault(mt, []).append(p["id"])

    # Meal Collections
    if force: await meal_collections.delete_many({})
    if await meal_collections.count_documents({}) == 0:
        for idx, mc in enumerate(MEAL_COLLECTIONS):
            req = []
            for k, label in mc["required_slot_keys"]:
                req.append({"slot_key": k, "label": label, "required": True,
                            "default_product_ids": prod_role_to_ids.get(k, [])[:1],
                            "substitute_product_ids": prod_role_to_ids.get(k, [])[1:5],
                            "quantity_hint": "1 pack"})
            opt = []
            for k, label in mc["optional_slot_keys"]:
                opt.append({"slot_key": k, "label": label, "required": False,
                            "default_product_ids": prod_role_to_ids.get(k, [])[:1],
                            "substitute_product_ids": prod_role_to_ids.get(k, [])[1:5],
                            "quantity_hint": "1 pack"})
            await meal_collections.insert_one({
                "id": new_id(), "title": mc["title"], "slug": mc["slug"],
                "description": mc["description"], "hero_image": mc["hero_image"],
                "meal_tag": mc["meal_tag"], "user_intent_phrases": mc["user_intent_phrases"],
                "required_slots": req, "optional_slots": opt,
                "protein_options": prod_role_to_ids.get("protein", []),
                "upsell_product_ids": prod_meal_to_ids.get(mc["meal_tag"], [])[:5],
                "recommended_bundle_id": None, "tier": "standard",
                "servings_default": mc["servings_default"],
                "spice_level_default": "medium",
                "active": True, "visible": True, "sort_order": idx,
                "created_at": utcnow_iso(),
            })

    # Bundles
    if force: await bundles.delete_many({})
    if await bundles.count_documents({}) == 0:
        for b in BUNDLES:
            items = []
            if b.get("meal_tag"):
                for pid in prod_meal_to_ids.get(b["meal_tag"], [])[:5]:
                    items.append({"product_id": pid, "quantity": 1, "required": True})
            await bundles.insert_one({
                "id": new_id(), "title": b["title"], "slug": b["slug"],
                "description": b["description"], "image": b["image"],
                "items": items, "optional_items": [],
                "price": b["price"], "compare_at_price": b["compare_at_price"],
                "discount_type": "fixed", "tier": b["tier"],
                "meal_tag": b.get("meal_tag"), "active": True, "created_at": utcnow_iso(),
            })

    # Collections
    if force: await collections_col.delete_many({})
    if await collections_col.count_documents({}) == 0:
        for idx, c in enumerate(COLLECTIONS):
            await collections_col.insert_one({
                "id": new_id(), "title": c["title"], "slug": c["slug"],
                "description": c["description"], "image": c["image"],
                "type": c["type"], "product_ids": [], "rules": None,
                "visible": True, "sort_order": idx, "created_at": utcnow_iso(),
            })

    # Templates + Automations
    if force:
        await message_templates.delete_many({})
        await automation_flows.delete_many({})
    if await message_templates.count_documents({}) == 0:
        for t in MESSAGE_TEMPLATES:
            await message_templates.insert_one({
                "id": new_id(), "channel": t["channel"], "name": t["name"],
                "subject": t["subject"], "body": t["body"],
                "variables": ["name", "order_number", "product", "days"],
                "active": True, "created_at": utcnow_iso(),
            })
    if await automation_flows.count_documents({}) == 0:
        for a in AUTOMATIONS:
            await automation_flows.insert_one({
                "id": new_id(), "name": a["name"], "trigger": a["trigger"],
                "channel": a["channel"], "template_id": None, "audience_segment": "all",
                "delay_minutes": a["delay_minutes"], "active": a["active"],
                "sent_count": 0, "opened_count": 0, "clicked_count": 0,
                "created_at": utcnow_iso(),
            })

    # Delivery zone
    if force: await delivery_zones.delete_many({})
    if await delivery_zones.count_documents({}) == 0:
        await delivery_zones.insert_one({
            "id": new_id(), "name": "Peterborough (5 miles)",
            "address": "1227 Bourges Blvd, Peterborough PE1 2AU",
            "store_lat": 52.5854, "store_lng": -0.2452,
            "radius_miles": 5, "per_mile_fee": 2.99,
            "free_threshold": 50, "active": True,
        })

    # Reviews
    if force: await reviews.delete_many({})
    if await reviews.count_documents({}) == 0:
        samples = [
            ("Chinwe O.", 5, "Best African supermarket in the UK", "My weekly jollof shop just got easier. Fast delivery and fresh."),
            ("Adebayo M.", 5, "Authentic and affordable", "Everything from palm oil to ehuru. Finally a proper African store online."),
            ("Funke A.", 4, "Loved the AI meal helper", "Told it I wanted pepper soup and it built my basket in 30 seconds."),
            ("Ngozi E.", 5, "Peterborough, we eat good!", "Frozen fish was perfect. Delivery within hours."),
            ("Tolu A.", 5, "Family-size packs save me money", "Bought the bulk oil bundle — great value."),
            ("Kemi L.", 5, "Shito is incredible", "Weeknight cooking has levelled up. Thank you Afrobean!"),
        ]
        cursor = products.find({"bestseller": True}, {"_id": 0, "id": 1}).limit(12)
        async for p in cursor:
            for n, r, t, b in samples[:3]:
                await reviews.insert_one({
                    "id": new_id(), "product_id": p["id"], "customer_id": None,
                    "customer_name": n, "rating": r, "title": t, "body": b,
                    "verified": True, "created_at": utcnow_iso(),
                })

    await audit_logs.insert_one({
        "id": new_id(), "actor_email": "system", "actor_role": "system",
        "action": "seed.complete", "target_type": "system", "target_id": None,
        "changes": None, "ip": None, "created_at": utcnow_iso(),
    })
