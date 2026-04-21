"""MongoDB connection and helpers."""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
admin_users = db.admin_users
customers = db.customers
categories = db.categories
products = db.products
collections_col = db.collections
meal_collections = db.meal_collections
bundles = db.bundles
carts = db.carts
orders = db.orders
ai_sessions = db.ai_sessions
message_templates = db.message_templates
automation_flows = db.automation_flows
audit_logs = db.audit_logs
wishlists = db.wishlists
reviews = db.reviews
delivery_zones = db.delivery_zones
payment_transactions = db.payment_transactions
otp_codes = db.otp_codes
imports = db.imports


def clean(doc):
    """Remove _id and return doc, works recursively for lists and dicts."""
    if isinstance(doc, list):
        return [clean(d) for d in doc]
    if isinstance(doc, dict):
        return {k: clean(v) for k, v in doc.items() if k != "_id"}
    return doc


async def ensure_indexes():
    await admin_users.create_index("email", unique=True)
    await customers.create_index("email", unique=True)
    await products.create_index("slug", unique=True)
    await products.create_index("category_id")
    await products.create_index("meal_tags")
    await categories.create_index("slug", unique=True)
    await collections_col.create_index("slug", unique=True)
    await meal_collections.create_index("slug", unique=True)
    await orders.create_index("order_number", unique=True)
    await orders.create_index("customer_id")
    await orders.create_index("stripe_session_id")
    await otp_codes.create_index("email")
