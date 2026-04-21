"""Seed data for Afrobean."""
import os
from datetime import datetime, timezone
from auth import hash_password
from db import (
    admin_users, customers, categories, products, collections_col,
    meal_collections, bundles, message_templates, automation_flows,
    delivery_zones, reviews, audit_logs,
)
from models import utcnow_iso, new_id


# ---------- Image pool (reliable Unsplash food images) ----------
IMG = {
    "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=80",
    "jollof": "https://images.pexels.com/photos/36707708/pexels-photo-36707708.jpeg?auto=compress&cs=tinysrgb&w=800",
    "palm_oil": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&q=80",
    "oil_generic": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=800&q=80",
    "spices": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=800&q=80",
    "spice_jar": "https://images.unsplash.com/photo-1532336414038-cf19250c5757?w=800&q=80",
    "beans": "https://images.unsplash.com/photo-1515543904379-3d757afe72e4?w=800&q=80",
    "flour": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=800&q=80",
    "plantain_chips": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=800&q=80",
    "drinks": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=800&q=80",
    "tea": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=800&q=80",
    "canned": "https://images.unsplash.com/photo-1584473457409-ce95a9c00017?w=800&q=80",
    "frozen_fish": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
    "frozen_meat": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=800&q=80",
    "beauty": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=800&q=80",
    "household": "https://images.unsplash.com/photo-1585060544812-6b45742d762f?w=800&q=80",
    "breakfast": "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?w=800&q=80",
    "milo": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=800&q=80",
    "custard": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&q=80",
    "garri": "https://images.unsplash.com/photo-1595475207225-428b62bda831?w=800&q=80",
    "yam_flour": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=800&q=80",
    "tomato_paste": "https://images.unsplash.com/photo-1599639668273-0a5a1b453acc?w=800&q=80",
    "chin_chin": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=800&q=80",
    "pepper_soup": "https://images.unsplash.com/photo-1583835746434-cf1534674b41?w=800&q=80",
    "stockfish": "https://images.unsplash.com/photo-1535007813616-79dc02ba4021?w=800&q=80",
    "egusi": "https://images.unsplash.com/photo-1615485925600-97237c4fc1ec?w=800&q=80",
    "seasoning": "https://images.unsplash.com/photo-1599909533730-d2a7651fce4d?w=800&q=80",
    "soap": "https://images.unsplash.com/photo-1600428877878-1a0fd85beda8?w=800&q=80",
    "shea": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=800&q=80",
}


# ---------- Categories ----------
CATEGORIES = [
    {"name": "Rice, Flour & Swallows", "slug": "rice-flour-swallows", "image": IMG["flour"], "sort_order": 1,
     "description": "Staple rice, flours, semovita, poundo, garri, and all your swallow essentials."},
    {"name": "Beans, Grains & Nuts", "slug": "beans-grains-nuts", "image": IMG["beans"], "sort_order": 2,
     "description": "Brown beans, black-eyed peas, groundnuts, and more."},
    {"name": "Oils & Cooking Essentials", "slug": "oils-cooking-essentials", "image": IMG["palm_oil"], "sort_order": 3,
     "description": "Palm oil, groundnut oil, vegetable oil, and cooking basics."},
    {"name": "Spices & Seasonings", "slug": "spices-seasonings", "image": IMG["spices"], "sort_order": 4,
     "description": "Authentic African spices and stock seasonings."},
    {"name": "Sauces, Pastes & Soup Bases", "slug": "sauces-pastes-soup-bases", "image": IMG["tomato_paste"], "sort_order": 5,
     "description": "Tomato pastes, banga base, egusi, ayamase and more."},
    {"name": "Breakfast & Cereals", "slug": "breakfast-cereals", "image": IMG["breakfast"], "sort_order": 6,
     "description": "Oats, pap, custard, cocoa beverages and breakfast staples."},
    {"name": "Drinks & Teas", "slug": "drinks-teas", "image": IMG["drinks"], "sort_order": 7,
     "description": "Malt drinks, ginger tea, hibiscus and juices."},
    {"name": "Snacks & Biscuits", "slug": "snacks-biscuits", "image": IMG["chin_chin"], "sort_order": 8,
     "description": "Chin chin, plantain chips, biscuits and treats."},
    {"name": "Canned Foods", "slug": "canned-foods", "image": IMG["canned"], "sort_order": 9,
     "description": "Canned tomatoes, sardines, corned beef and more."},
    {"name": "Frozen Fish & Meat", "slug": "frozen-fish-meat", "image": IMG["frozen_fish"], "sort_order": 10,
     "description": "Frozen croaker, tilapia, goat meat and poultry."},
    {"name": "Beauty & Personal Care", "slug": "beauty-personal-care", "image": IMG["shea"], "sort_order": 11,
     "description": "Shea butter, black soap, hair products and personal care."},
    {"name": "Household Essentials", "slug": "household-essentials", "image": IMG["household"], "sort_order": 12,
     "description": "Kitchen and cleaning essentials for your home."},
]


def _variants(default_price, sku_prefix, extra_sizes=None):
    """Build pack-size variants."""
    variants = [
        {"size_label": "Standard", "pack_class": "single", "price": default_price,
         "compare_at_price": None, "sku": f"{sku_prefix}-STD", "stock": 45, "is_default": True, "is_best_value": False},
    ]
    if extra_sizes:
        for s in extra_sizes:
            variants.append(s)
    return variants


def _product(name, slug, category_slug, price, img_key, *, brand="Afrobean", meal_tags=None,
             roles=None, tags=None, bestseller=False, featured=False, new_arrival=False,
             compare_at=None, cost=None, description="", extra_variants=None, subcategory=None,
             sku=None, stock=50, status="active"):
    sku = sku or f"AFB-{slug.upper().replace('-','')[:10]}"
    variants = _variants(price, sku, extra_variants)
    return {
        "name": name, "slug": slug, "brand": brand,
        "category_slug": category_slug, "subcategory": subcategory,
        "price": price, "compare_at_price": compare_at, "cost_price": cost,
        "images": [IMG.get(img_key, IMG["rice"])],
        "tags": tags or [], "cuisine_tags": ["african", "nigerian", "west-african"],
        "meal_tags": meal_tags or [], "ai_meal_roles": roles or [],
        "variants": variants, "sku": sku, "stock": stock,
        "featured": featured, "bestseller": bestseller, "new_arrival": new_arrival,
        "status": status,
        "description": description or f"Authentic {name} — a staple for African kitchens, delivered fresh to your door in Peterborough.",
    }


PRODUCTS = [
    # Rice, Flour & Swallows
    _product("Premium Long Grain Parboiled Rice 5kg", "premium-long-grain-rice-5kg", "rice-flour-swallows", 13.99, "rice",
             meal_tags=["jollof"], roles=["rice_base"], bestseller=True, featured=True, compare_at=15.99, cost=9.50,
             extra_variants=[{"size_label": "10kg Family", "pack_class": "family", "price": 24.99, "sku": "AFB-RICE-10KG", "stock": 30, "is_default": False, "is_best_value": True},
                             {"size_label": "25kg Bulk", "pack_class": "bulk", "price": 54.99, "sku": "AFB-RICE-25KG", "stock": 15, "is_default": False, "is_best_value": False}]),
    _product("Basmati Rice 5kg", "basmati-rice-5kg", "rice-flour-swallows", 15.99, "rice", roles=["rice_base"], tags=["basmati"]),
    _product("Tolaram Yam Flour (Poundo Iyam) 1.8kg", "poundo-iyam-yam-flour", "rice-flour-swallows", 6.99, "yam_flour",
             meal_tags=["swallow"], roles=["swallow"], bestseller=True, brand="Tolaram"),
    _product("Plantain Flour 1kg", "plantain-flour-1kg", "rice-flour-swallows", 5.49, "flour", meal_tags=["swallow"], roles=["swallow"]),
    _product("Semovita 1kg", "semovita-1kg", "rice-flour-swallows", 4.99, "flour", meal_tags=["swallow"], roles=["swallow"], brand="Golden Penny"),
    _product("Ijebu Garri 1kg", "ijebu-garri-1kg", "rice-flour-swallows", 4.29, "garri", meal_tags=["swallow"], roles=["swallow"], bestseller=True),
    _product("White Garri 5kg", "white-garri-5kg", "rice-flour-swallows", 11.99, "garri", meal_tags=["swallow"], roles=["swallow"],
             extra_variants=[{"size_label": "10kg Family", "pack_class": "family", "price": 19.99, "sku": "AFB-GARRI-10", "stock": 20, "is_default": False, "is_best_value": True}]),
    _product("Ofada Rice 2kg", "ofada-rice-2kg", "rice-flour-swallows", 12.49, "rice", roles=["rice_base"], featured=True, new_arrival=True),
    _product("Wheat Flour 1.5kg", "wheat-flour-1-5kg", "rice-flour-swallows", 5.99, "flour", roles=["swallow"]),
    _product("Fufu Flour 1kg", "fufu-flour-1kg", "rice-flour-swallows", 4.79, "flour", meal_tags=["swallow"], roles=["swallow"]),

    # Beans, Grains & Nuts
    _product("Premium Nigerian Brown Beans 2kg", "brown-beans-2kg", "beans-grains-nuts", 8.99, "beans",
             meal_tags=["moi_moi"], roles=["beans"], bestseller=True, featured=True),
    _product("Honey Beans (Oloyin) 1kg", "honey-beans-oloyin-1kg", "beans-grains-nuts", 5.49, "beans",
             meal_tags=["moi_moi"], roles=["beans"]),
    _product("Black-Eyed Peas 1kg", "black-eyed-peas-1kg", "beans-grains-nuts", 4.99, "beans",
             meal_tags=["moi_moi"], roles=["beans"]),
    _product("Roasted Groundnuts 500g", "roasted-groundnuts-500g", "beans-grains-nuts", 3.99, "beans", tags=["snack"]),
    _product("Egusi Seeds (Ground) 400g", "egusi-seeds-ground", "beans-grains-nuts", 6.49, "egusi",
             meal_tags=["egusi"], roles=["egusi_base"]),

    # Oils & Cooking Essentials
    _product("Zomi Palm Oil 1L", "zomi-palm-oil-1l", "oils-cooking-essentials", 6.99, "palm_oil",
             meal_tags=["jollof", "banga", "efo_riro", "moi_moi"], roles=["oil", "palm_oil"], bestseller=True,
             extra_variants=[{"size_label": "2L Family", "pack_class": "family", "price": 12.99, "sku": "AFB-PALM-2L", "stock": 40, "is_default": False, "is_best_value": True},
                             {"size_label": "5L Bulk", "pack_class": "bulk", "price": 28.99, "sku": "AFB-PALM-5L", "stock": 20, "is_default": False, "is_best_value": False}]),
    _product("Groundnut Oil 1L", "groundnut-oil-1l", "oils-cooking-essentials", 7.49, "oil_generic",
             meal_tags=["jollof"], roles=["oil"]),
    _product("Vegetable Oil 2L", "vegetable-oil-2l", "oils-cooking-essentials", 7.99, "oil_generic",
             meal_tags=["jollof"], roles=["oil"], bestseller=True),
    _product("Locust Beans (Iru) 100g", "locust-beans-iru", "oils-cooking-essentials", 4.29, "spices",
             meal_tags=["efo_riro"], roles=["iru"]),

    # Spices & Seasonings
    _product("Afrobean Jollof Spice Mix 100g", "afrobean-jollof-spice", "spices-seasonings", 3.49, "spice_jar",
             meal_tags=["jollof"], roles=["jollof_seasoning"], bestseller=True, featured=True, new_arrival=True),
    _product("Pepper Soup Spice Mix 100g", "pepper-soup-spice", "spices-seasonings", 3.49, "spice_jar",
             meal_tags=["pepper_soup"], roles=["pepper_soup_spice"], bestseller=True, featured=True),
    _product("Banga Spice Mix 100g", "banga-spice-mix", "spices-seasonings", 3.99, "spice_jar",
             meal_tags=["banga"], roles=["banga_spice"]),
    _product("Efo Riro Spice Mix 80g", "efo-riro-spice", "spices-seasonings", 3.79, "spice_jar",
             meal_tags=["efo_riro"], roles=["efo_riro_spice"]),
    _product("Curry Powder 100g", "curry-powder-100g", "spices-seasonings", 2.99, "spices",
             meal_tags=["jollof"], roles=["curry"]),
    _product("Dried Thyme 50g", "dried-thyme-50g", "spices-seasonings", 2.49, "spices",
             meal_tags=["jollof", "pepper_soup"], roles=["thyme"]),
    _product("Maggi Star Stock Cubes (20pk)", "maggi-star-cubes-20", "spices-seasonings", 3.29, "seasoning",
             meal_tags=["jollof", "pepper_soup", "moi_moi", "banga", "efo_riro"], roles=["stock_seasoning"], bestseller=True),
    _product("Ehuru (Calabash Nutmeg) 50g", "ehuru-calabash-nutmeg", "spices-seasonings", 3.99, "spices",
             meal_tags=["pepper_soup"], roles=["ehuru"]),
    _product("Alligator Pepper 50g", "alligator-pepper-50g", "spices-seasonings", 3.49, "spices",
             meal_tags=["pepper_soup"], roles=["alligator_pepper"]),
    _product("Uziza Seeds 50g", "uziza-seeds-50g", "spices-seasonings", 3.29, "spices",
             meal_tags=["pepper_soup"], roles=["uziza"]),
    _product("Ground Crayfish 200g", "ground-crayfish-200g", "spices-seasonings", 4.99, "spices",
             meal_tags=["moi_moi", "efo_riro", "banga"], roles=["crayfish"], bestseller=True),
    _product("Cameroon Pepper 100g", "cameroon-pepper-100g", "spices-seasonings", 4.49, "spices", roles=["pepper"]),

    # Sauces, Pastes & Soup Bases
    _product("Tomato Paste Double Concentrate 400g", "tomato-paste-400g", "sauces-pastes-soup-bases", 2.99, "tomato_paste",
             meal_tags=["jollof", "efo_riro"], roles=["tomato_base"], bestseller=True,
             extra_variants=[{"size_label": "800g Family", "pack_class": "family", "price": 5.29, "sku": "AFB-TOM-800", "stock": 40, "is_default": False, "is_best_value": True}]),
    _product("Palm-Fruit (Banga) Base 800g", "banga-base-800g", "sauces-pastes-soup-bases", 6.99, "palm_oil",
             meal_tags=["banga"], roles=["banga_base"], featured=True),
    _product("Ayamase Sauce Base 500g", "ayamase-sauce-base", "sauces-pastes-soup-bases", 7.49, "tomato_paste",
             meal_tags=["jollof"], roles=["sauce_base"], new_arrival=True),
    _product("Moi Moi Cooking Pouches (50pk)", "moi-moi-pouches-50pk", "sauces-pastes-soup-bases", 4.49, "canned",
             meal_tags=["moi_moi"], roles=["moi_moi_pouch"]),
    _product("Leaf Spinach (Frozen) 500g", "leaf-spinach-frozen-500g", "sauces-pastes-soup-bases", 3.49, "canned",
             meal_tags=["efo_riro"], roles=["efo_leaves"]),

    # Breakfast & Cereals
    _product("Quaker Oats 1kg", "quaker-oats-1kg", "breakfast-cereals", 5.99, "breakfast",
             meal_tags=["breakfast"], roles=["oats"], bestseller=True, brand="Quaker"),
    _product("Custard Powder 500g", "custard-powder-500g", "breakfast-cereals", 3.99, "custard",
             meal_tags=["breakfast"], roles=["custard"], brand="Checkers"),
    _product("Ogi / Pap Mix 1kg", "ogi-pap-mix", "breakfast-cereals", 5.49, "breakfast",
             meal_tags=["breakfast"], roles=["pap"]),
    _product("Milo Chocolate Drink 400g", "milo-400g", "breakfast-cereals", 5.99, "milo",
             meal_tags=["breakfast"], roles=["cocoa"], bestseller=True, brand="Nestlé",
             extra_variants=[{"size_label": "900g Family", "pack_class": "family", "price": 10.99, "sku": "AFB-MILO-900", "stock": 30, "is_default": False, "is_best_value": True}]),
    _product("Bournvita 450g", "bournvita-450g", "breakfast-cereals", 5.49, "milo",
             meal_tags=["breakfast"], roles=["cocoa"], brand="Cadbury"),
    _product("Peak Milk Powder 900g Tin", "peak-milk-900g", "breakfast-cereals", 12.99, "breakfast",
             meal_tags=["breakfast"], roles=["milk"], bestseller=True, brand="Peak"),
    _product("Nigerian Cornflakes 500g", "nigerian-cornflakes-500g", "breakfast-cereals", 4.99, "breakfast",
             meal_tags=["breakfast"], roles=["cereal"]),

    # Drinks & Teas
    _product("Maltina Malt Drink (Can) 330ml x6", "maltina-6pack", "drinks-teas", 7.99, "drinks", tags=["drinks"]),
    _product("Supermalt 330ml x6", "supermalt-6pack", "drinks-teas", 7.49, "drinks", tags=["drinks"], bestseller=True),
    _product("Hibiscus (Zobo) Leaves 250g", "zobo-leaves-250g", "drinks-teas", 4.99, "tea"),
    _product("Ginger Tea Bags (30pk)", "ginger-tea-30", "drinks-teas", 3.99, "tea", tags=["tea"]),
    _product("Chapman Drink Mix 1L", "chapman-mix-1l", "drinks-teas", 5.49, "drinks", new_arrival=True),

    # Snacks
    _product("Chin Chin Crunchy 500g", "chin-chin-500g", "snacks-biscuits", 4.49, "chin_chin", tags=["snacks"], bestseller=True),
    _product("Plantain Chips 200g", "plantain-chips-200g", "snacks-biscuits", 2.99, "plantain_chips", tags=["snacks"], bestseller=True),
    _product("Gala Sausage Roll (10pk)", "gala-10pk", "snacks-biscuits", 5.99, "chin_chin", tags=["snacks"]),
    _product("Cabin Biscuits 500g", "cabin-biscuits-500g", "snacks-biscuits", 3.99, "chin_chin", tags=["biscuits"]),

    # Canned Foods
    _product("Geisha Sardines in Tomato 125g", "geisha-sardines-125g", "canned-foods", 1.99, "canned"),
    _product("Titus Sardines 125g", "titus-sardines-125g", "canned-foods", 1.89, "canned", bestseller=True),
    _product("Corned Beef 340g", "corned-beef-340g", "canned-foods", 4.99, "canned"),
    _product("Canned Tomatoes 400g", "canned-tomatoes-400g", "canned-foods", 1.49, "canned"),

    # Frozen Fish & Meat
    _product("Frozen Croaker Fish 1kg", "frozen-croaker-1kg", "frozen-fish-meat", 12.99, "frozen_fish",
             meal_tags=["pepper_soup"], roles=["protein"], bestseller=True, featured=True),
    _product("Frozen Tilapia 1kg", "frozen-tilapia-1kg", "frozen-fish-meat", 10.99, "frozen_fish",
             meal_tags=["pepper_soup"], roles=["protein"]),
    _product("Frozen Mackerel 1kg", "frozen-mackerel-1kg", "frozen-fish-meat", 8.99, "frozen_fish",
             meal_tags=["pepper_soup"], roles=["protein"]),
    _product("Stock Fish (Dried) 200g", "stock-fish-200g", "frozen-fish-meat", 9.99, "stockfish",
             meal_tags=["efo_riro", "banga"], roles=["protein"]),
    _product("Frozen Goat Meat 1kg", "frozen-goat-meat-1kg", "frozen-fish-meat", 14.99, "frozen_meat",
             meal_tags=["pepper_soup", "efo_riro", "banga"], roles=["protein"]),
    _product("Frozen Chicken Drums 1kg", "frozen-chicken-drums-1kg", "frozen-fish-meat", 6.99, "frozen_meat",
             meal_tags=["jollof", "pepper_soup"], roles=["protein"], bestseller=True),
    _product("Frozen Snails 500g", "frozen-snails-500g", "frozen-fish-meat", 13.99, "frozen_meat", roles=["protein"]),

    # Beauty
    _product("Raw Shea Butter 250g", "raw-shea-butter-250g", "beauty-personal-care", 6.99, "shea", new_arrival=True),
    _product("African Black Soap 150g", "african-black-soap-150g", "beauty-personal-care", 4.49, "soap", bestseller=True),
    _product("Dudu-Osun Natural Soap (4pk)", "dudu-osun-4pk", "beauty-personal-care", 8.99, "soap"),

    # Household
    _product("Jumbo Dishwashing Liquid 1L", "jumbo-dish-soap-1l", "household-essentials", 3.49, "household"),
    _product("Kitchen Paper Towels (6pk)", "kitchen-towels-6pk", "household-essentials", 5.99, "household"),
]


# ---------- Meal Collections ----------
MEAL_COLLECTIONS = [
    {
        "title": "Jollof Rice Essentials",
        "slug": "jollof-rice-essentials",
        "description": "Everything you need for a pot of party-perfect Jollof rice.",
        "hero_image": IMG["jollof"],
        "meal_tag": "jollof",
        "user_intent_phrases": ["jollof rice", "make jollof", "cook jollof", "party jollof", "nigerian jollof"],
        "required_slot_keys": [
            ("rice_base", "Long grain rice"),
            ("tomato_base", "Tomato paste / base"),
            ("jollof_seasoning", "Jollof spice mix"),
            ("curry", "Curry powder"),
            ("thyme", "Thyme"),
            ("oil", "Cooking oil"),
            ("stock_seasoning", "Stock seasoning"),
        ],
        "optional_slot_keys": [("protein", "Choose your protein")],
        "tier": "standard",
        "servings_default": 5,
    },
    {
        "title": "Pepper Soup Essentials",
        "slug": "pepper-soup-essentials",
        "description": "Spicy, aromatic pepper soup — the full ingredient list.",
        "hero_image": IMG["pepper_soup"],
        "meal_tag": "pepper_soup",
        "user_intent_phrases": ["pepper soup", "ngwo-ngwo", "peppersoup", "catfish pepper soup"],
        "required_slot_keys": [
            ("pepper_soup_spice", "Pepper soup spice"),
            ("stock_seasoning", "Stock seasoning"),
            ("protein", "Protein (fish/meat)"),
        ],
        "optional_slot_keys": [
            ("ehuru", "Ehuru (calabash nutmeg)"),
            ("alligator_pepper", "Alligator pepper"),
            ("uziza", "Uziza seeds"),
            ("swallow", "Swallow of choice"),
        ],
        "tier": "standard",
        "servings_default": 4,
    },
    {
        "title": "Moi Moi Essentials",
        "slug": "moi-moi-essentials",
        "description": "Steamed bean pudding — everything from beans to pouches.",
        "hero_image": IMG["beans"],
        "meal_tag": "moi_moi",
        "user_intent_phrases": ["moi moi", "moin moin", "bean pudding"],
        "required_slot_keys": [
            ("beans", "Peeled beans"),
            ("oil", "Palm oil"),
            ("stock_seasoning", "Seasoning"),
            ("moi_moi_pouch", "Cooking pouches"),
        ],
        "optional_slot_keys": [
            ("protein", "Fish / egg"),
            ("crayfish", "Ground crayfish"),
        ],
        "tier": "standard",
        "servings_default": 6,
    },
    {
        "title": "Banga Soup Essentials",
        "slug": "banga-soup-essentials",
        "description": "Rich palm-fruit soup, perfect with starch or eba.",
        "hero_image": IMG["palm_oil"],
        "meal_tag": "banga",
        "user_intent_phrases": ["banga", "banga soup", "ofe akwu"],
        "required_slot_keys": [
            ("banga_base", "Palm-fruit base"),
            ("banga_spice", "Banga spice"),
            ("stock_seasoning", "Seasoning"),
            ("protein", "Protein (fish/meat)"),
        ],
        "optional_slot_keys": [
            ("swallow", "Swallow of choice"),
            ("crayfish", "Ground crayfish"),
        ],
        "tier": "standard",
        "servings_default": 4,
    },
    {
        "title": "Efo Riro Essentials",
        "slug": "efo-riro-essentials",
        "description": "Rich Yoruba spinach stew with everything you need.",
        "hero_image": IMG["spices"],
        "meal_tag": "efo_riro",
        "user_intent_phrases": ["efo riro", "vegetable soup", "efo"],
        "required_slot_keys": [
            ("efo_leaves", "Leaf spinach"),
            ("tomato_base", "Tomato base"),
            ("efo_riro_spice", "Efo riro spice"),
            ("palm_oil", "Palm oil"),
            ("stock_seasoning", "Seasoning"),
            ("protein", "Protein (fish/meat)"),
        ],
        "optional_slot_keys": [
            ("iru", "Locust beans (iru)"),
            ("crayfish", "Ground crayfish"),
        ],
        "tier": "standard",
        "servings_default": 4,
    },
    {
        "title": "Breakfast Staples",
        "slug": "breakfast-staples",
        "description": "Everything for a week of beautiful African breakfasts.",
        "hero_image": IMG["breakfast"],
        "meal_tag": "breakfast",
        "user_intent_phrases": ["breakfast", "pap", "custard", "oats", "milo"],
        "required_slot_keys": [
            ("oats", "Oats"),
            ("pap", "Pap / ogi"),
            ("custard", "Custard"),
            ("milk", "Milk powder"),
            ("cocoa", "Cocoa beverage"),
        ],
        "optional_slot_keys": [
            ("cereal", "Cornflakes"),
        ],
        "tier": "standard",
        "servings_default": 4,
    },
]


# ---------- Bundles ----------
BUNDLES = [
    {"title": "Jollof Rice Combo", "slug": "jollof-rice-combo", "meal_tag": "jollof",
     "description": "Everything you need for 5 servings of Jollof rice.",
     "image": IMG["jollof"], "price": 29.99, "compare_at_price": 35.50, "tier": "standard"},
    {"title": "Pepper Soup Combo", "slug": "pepper-soup-combo", "meal_tag": "pepper_soup",
     "description": "Pepper soup spices + protein bundle.",
     "image": IMG["pepper_soup"], "price": 24.99, "compare_at_price": 29.50, "tier": "standard"},
    {"title": "Family Swallow Bundle", "slug": "family-swallow-bundle",
     "description": "Yam flour, garri, semovita & plantain flour — family-size pack.",
     "image": IMG["yam_flour"], "price": 22.99, "compare_at_price": 26.50, "tier": "family"},
    {"title": "Breakfast Combo", "slug": "breakfast-combo", "meal_tag": "breakfast",
     "description": "Oats, pap, custard, milk & Milo — a week of breakfasts.",
     "image": IMG["breakfast"], "price": 27.99, "compare_at_price": 32.00, "tier": "standard"},
    {"title": "Bulk Oil Bundle", "slug": "bulk-oil-bundle",
     "description": "Palm oil + groundnut oil + vegetable oil bulk pack.",
     "image": IMG["palm_oil"], "price": 33.99, "compare_at_price": 39.50, "tier": "family"},
    {"title": "Student Pantry Bundle", "slug": "student-pantry-bundle",
     "description": "Starter pantry essentials for students.",
     "image": IMG["rice"], "price": 39.99, "compare_at_price": 47.00, "tier": "student"},
    {"title": "New Customer Starter Box", "slug": "new-customer-starter-box",
     "description": "Welcome to Afrobean — top picks across the store.",
     "image": IMG["spices"], "price": 49.99, "compare_at_price": 59.00, "tier": "premium"},
]


COLLECTIONS = [
    {"title": "Best Sellers", "slug": "best-sellers", "type": "smart",
     "description": "Our most-loved products in Peterborough.", "image": IMG["jollof"]},
    {"title": "New Arrivals", "slug": "new-arrivals", "type": "smart",
     "description": "Fresh additions to the Afrobean pantry.", "image": IMG["spices"]},
    {"title": "Pantry Restock", "slug": "pantry-restock", "type": "manual",
     "description": "Top up on your weekly essentials.", "image": IMG["rice"]},
    {"title": "Family-Size Value", "slug": "family-size-value", "type": "manual",
     "description": "Family-size packs that save you money.", "image": IMG["flour"]},
    {"title": "Bulk Buy Picks", "slug": "bulk-buy-picks", "type": "manual",
     "description": "Big packs for bigger savings.", "image": IMG["palm_oil"]},
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
     "body": "Hi {name}, it's been {days} days since your last order. Restock your pantry essentials."},
    {"channel": "email", "name": "Meal Campaign — Jollof", "subject": "Cook jollof this weekend",
     "body": "Hi {name}, shop our Jollof Essentials collection and get everything in one click."},
]


AUTOMATIONS = [
    {"name": "Welcome new customers", "trigger": "welcome", "channel": "email", "delay_minutes": 0, "active": True},
    {"name": "Recover abandoned cart", "trigger": "abandoned_cart", "channel": "email", "delay_minutes": 60, "active": True},
    {"name": "Post-purchase thank you", "trigger": "order_placed", "channel": "email", "delay_minutes": 5, "active": True},
    {"name": "Order shipped WhatsApp", "trigger": "order_shipped", "channel": "whatsapp", "delay_minutes": 0, "active": True},
    {"name": "30-day pantry replenishment", "trigger": "replenishment", "channel": "email", "delay_minutes": 60 * 24 * 30, "active": False},
    {"name": "Back-in-stock notification", "trigger": "back_in_stock", "channel": "email", "delay_minutes": 0, "active": True},
    {"name": "Jollof weekend campaign", "trigger": "meal_campaign", "channel": "email", "delay_minutes": 0, "active": False},
]


async def seed_all(force: bool = False):
    # Admin users
    if force:
        await admin_users.delete_many({})
    if await admin_users.count_documents({}) == 0:
        await admin_users.insert_one({
            "id": new_id(),
            "email": "admin@afrobean.co.uk",
            "name": "Afrobean Admin",
            "role": "super_admin",
            "password_hash": hash_password("Admin@123"),
            "active": True,
            "created_at": utcnow_iso(),
        })
        await admin_users.insert_one({
            "id": new_id(),
            "email": "merch@afrobean.co.uk",
            "name": "Merchandiser User",
            "role": "merchandiser",
            "password_hash": hash_password("Merch@123"),
            "active": True,
            "created_at": utcnow_iso(),
        })

    # Customers
    if force:
        await customers.delete_many({})
    if await customers.count_documents({}) == 0:
        await customers.insert_one({
            "id": new_id(),
            "email": "demo@afrobean.co.uk",
            "name": "Demo Shopper",
            "phone": "07700900123",
            "password_hash": hash_password("Demo@123"),
            "email_consent": True, "whatsapp_consent": True, "marketing_consent": True,
            "addresses": [{"line1": "45 Westgate", "city": "Peterborough", "postcode": "PE1 1PY", "country": "UK"}],
            "created_at": utcnow_iso(),
            "active": True, "total_spend": 0, "order_count": 0,
        })

    # Categories
    if force:
        await categories.delete_many({})
    cat_map = {}
    if await categories.count_documents({}) == 0:
        for idx, c in enumerate(CATEGORIES):
            doc = {
                "id": new_id(), "name": c["name"], "slug": c["slug"],
                "description": c["description"], "image": c["image"],
                "sort_order": c["sort_order"], "visible": True,
                "seo_title": c["name"], "seo_description": c["description"],
                "parent_id": None, "created_at": utcnow_iso(),
            }
            await categories.insert_one(doc)
            cat_map[c["slug"]] = doc["id"]
    else:
        async for c in categories.find({}, {"_id": 0}):
            cat_map[c["slug"]] = c["id"]

    # Products
    if force:
        await products.delete_many({})
    prod_slug_to_id = {}
    prod_role_to_ids = {}  # role -> list of product ids
    prod_meal_to_ids = {}  # meal_tag -> list
    if await products.count_documents({}) == 0:
        for p in PRODUCTS:
            doc = {
                "id": new_id(),
                "name": p["name"], "slug": p["slug"], "brand": p["brand"],
                "description": p["description"],
                "category_id": cat_map.get(p["category_slug"]),
                "subcategory_id": None,
                "images": p["images"],
                "tags": p["tags"], "cuisine_tags": p["cuisine_tags"],
                "meal_tags": p["meal_tags"], "dietary_tags": [],
                "use_case_tags": [], "collection_tags": [],
                "ai_meal_roles": p["ai_meal_roles"],
                "variants": p["variants"],
                "price": p["price"], "compare_at_price": p["compare_at_price"],
                "cost_price": p["cost_price"] or round(p["price"] * 0.6, 2),
                "sku": p["sku"], "barcode": "",
                "stock": p["stock"], "low_stock_threshold": 5, "reorder_threshold": 10,
                "related_product_ids": [], "upsell_product_ids": [], "substitute_product_ids": [],
                "featured": p["featured"], "bestseller": p["bestseller"],
                "new_arrival": p["new_arrival"], "bundle_eligible": True,
                "status": p["status"],
                "avg_rating": 4.6 if p["bestseller"] else 4.4,
                "review_count": 124 if p["bestseller"] else 32,
                "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
            }
            await products.insert_one(doc)
            prod_slug_to_id[p["slug"]] = doc["id"]
            for role in p["ai_meal_roles"]:
                prod_role_to_ids.setdefault(role, []).append(doc["id"])
            for mt in p["meal_tags"]:
                prod_meal_to_ids.setdefault(mt, []).append(doc["id"])
    else:
        async for p in products.find({}, {"_id": 0}):
            prod_slug_to_id[p["slug"]] = p["id"]
            for role in p.get("ai_meal_roles", []):
                prod_role_to_ids.setdefault(role, []).append(p["id"])
            for mt in p.get("meal_tags", []):
                prod_meal_to_ids.setdefault(mt, []).append(p["id"])

    # Meal Collections
    if force:
        await meal_collections.delete_many({})
    if await meal_collections.count_documents({}) == 0:
        for idx, mc in enumerate(MEAL_COLLECTIONS):
            req_slots = []
            for slot_key, label in mc["required_slot_keys"]:
                req_slots.append({
                    "slot_key": slot_key, "label": label, "required": True,
                    "default_product_ids": prod_role_to_ids.get(slot_key, [])[:1],
                    "substitute_product_ids": prod_role_to_ids.get(slot_key, [])[1:4],
                    "quantity_hint": "1 pack",
                })
            opt_slots = []
            for slot_key, label in mc["optional_slot_keys"]:
                opt_slots.append({
                    "slot_key": slot_key, "label": label, "required": False,
                    "default_product_ids": prod_role_to_ids.get(slot_key, [])[:1],
                    "substitute_product_ids": prod_role_to_ids.get(slot_key, [])[1:4],
                    "quantity_hint": "1 pack",
                })
            doc = {
                "id": new_id(),
                "title": mc["title"], "slug": mc["slug"], "description": mc["description"],
                "hero_image": mc["hero_image"], "meal_tag": mc["meal_tag"],
                "user_intent_phrases": mc["user_intent_phrases"],
                "required_slots": req_slots, "optional_slots": opt_slots,
                "protein_options": prod_role_to_ids.get("protein", []),
                "upsell_product_ids": prod_meal_to_ids.get(mc["meal_tag"], [])[:4],
                "recommended_bundle_id": None,
                "tier": mc["tier"], "servings_default": mc["servings_default"],
                "spice_level_default": "medium",
                "active": True, "visible": True, "sort_order": idx,
                "created_at": utcnow_iso(),
            }
            await meal_collections.insert_one(doc)

    # Bundles
    if force:
        await bundles.delete_many({})
    if await bundles.count_documents({}) == 0:
        for b in BUNDLES:
            items = []
            if b.get("meal_tag"):
                for pid in prod_meal_to_ids.get(b["meal_tag"], [])[:5]:
                    items.append({"product_id": pid, "quantity": 1, "required": True})
            doc = {
                "id": new_id(),
                "title": b["title"], "slug": b["slug"], "description": b["description"],
                "image": b["image"], "items": items, "optional_items": [],
                "price": b["price"], "compare_at_price": b["compare_at_price"],
                "discount_type": "fixed", "tier": b["tier"],
                "meal_tag": b.get("meal_tag"), "active": True, "created_at": utcnow_iso(),
            }
            await bundles.insert_one(doc)

    # Collections
    if force:
        await collections_col.delete_many({})
    if await collections_col.count_documents({}) == 0:
        for idx, c in enumerate(COLLECTIONS):
            doc = {
                "id": new_id(), "title": c["title"], "slug": c["slug"],
                "description": c["description"], "image": c["image"],
                "type": c["type"], "product_ids": [], "rules": None,
                "visible": True, "sort_order": idx, "created_at": utcnow_iso(),
            }
            await collections_col.insert_one(doc)

    # Templates & Automations
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

    # Delivery Zone
    if force:
        await delivery_zones.delete_many({})
    if await delivery_zones.count_documents({}) == 0:
        await delivery_zones.insert_one({
            "id": new_id(), "name": "Peterborough (5 miles)",
            "address": "1227 Bourges Blvd, Peterborough PE1 2AU",
            "radius_miles": 5, "per_mile_fee": 2.99,
            "free_threshold": 50, "active": True,
        })

    # Reviews
    if force:
        await reviews.delete_many({})
    if await reviews.count_documents({}) == 0:
        samples = [
            ("Chinwe O.", 5, "Best African supermarket in the UK", "My weekly jollof shop just got easier. Fast delivery and fresh."),
            ("Adebayo M.", 5, "Authentic and affordable", "Everything from palm oil to ehuru. Finally a proper African store online."),
            ("Funke A.", 4, "Loved the AI meal helper", "Told it I wanted pepper soup and it built my basket in 30 seconds."),
            ("Ngozi E.", 5, "Peterborough, we eat good!", "Frozen croaker was perfect. Delivery was within hours."),
            ("Tolu A.", 5, "Family-size packs save me money", "Bought the 10kg rice + palm oil bundle — great value."),
            ("Kemi L.", 5, "Ayamase base is incredible", "Weeknight cooking has levelled up. Thank you Afrobean!"),
        ]
        async for p in products.find({"bestseller": True}, {"_id": 0, "id": 1}).limit(8):
            pid = p["id"]
            for i, (n, r, t, b) in enumerate(samples[:3]):
                await reviews.insert_one({
                    "id": new_id(), "product_id": pid, "customer_id": None,
                    "customer_name": n, "rating": r, "title": t, "body": b,
                    "verified": True, "created_at": utcnow_iso(),
                })

    # Audit log seed
    await audit_logs.insert_one({
        "id": new_id(), "actor_email": "system", "actor_role": "system",
        "action": "seed.complete", "target_type": "system", "target_id": None,
        "changes": None, "ip": None, "created_at": utcnow_iso(),
    })
