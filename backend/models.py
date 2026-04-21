"""Pydantic models for Afrobean."""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timezone
import uuid


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


# ---------- Users & Customers ----------
class AdminUser(BaseModel):
    id: str = Field(default_factory=new_id)
    email: EmailStr
    name: str
    role: Literal[
        "super_admin", "merchandiser", "inventory_manager",
        "operations", "support", "marketing", "analyst"
    ] = "super_admin"
    password_hash: str
    active: bool = True
    created_at: str = Field(default_factory=utcnow_iso)


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class Customer(BaseModel):
    id: str = Field(default_factory=new_id)
    email: EmailStr
    name: Optional[str] = ""
    phone: Optional[str] = ""
    password_hash: Optional[str] = None
    marketing_consent: bool = False
    whatsapp_consent: bool = False
    email_consent: bool = True
    addresses: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=utcnow_iso)
    active: bool = True
    total_spend: float = 0.0
    order_count: int = 0


class CustomerSignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    phone: Optional[str] = ""


class CustomerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str


# ---------- Catalogue ----------
class Category(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    slug: str
    description: Optional[str] = ""
    image: Optional[str] = ""
    icon: Optional[str] = ""
    sort_order: int = 0
    visible: bool = True
    seo_title: Optional[str] = ""
    seo_description: Optional[str] = ""
    parent_id: Optional[str] = None  # for subcategories
    created_at: str = Field(default_factory=utcnow_iso)


class PackSizeVariant(BaseModel):
    size_label: str  # e.g. "500g", "1kg", "Family 2kg"
    pack_class: Literal["single", "family", "bulk", "wholesale"] = "single"
    price: float
    compare_at_price: Optional[float] = None
    sku: str
    stock: int = 0
    is_default: bool = False
    is_best_value: bool = False


class Product(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    slug: str
    brand: Optional[str] = ""
    description: str = ""
    category_id: str
    subcategory_id: Optional[str] = None
    images: List[str] = []
    tags: List[str] = []
    cuisine_tags: List[str] = []
    meal_tags: List[str] = []  # e.g. ["jollof", "pepper_soup"]
    dietary_tags: List[str] = []
    use_case_tags: List[str] = []
    collection_tags: List[str] = []
    ai_meal_roles: List[str] = []  # slots this product can fill e.g. "rice_base"
    variants: List[PackSizeVariant] = []
    price: float = 0  # default (first variant)
    compare_at_price: Optional[float] = None
    cost_price: Optional[float] = None
    sku: str = ""
    barcode: Optional[str] = ""
    stock: int = 0
    low_stock_threshold: int = 5
    reorder_threshold: int = 10
    related_product_ids: List[str] = []
    upsell_product_ids: List[str] = []
    substitute_product_ids: List[str] = []
    featured: bool = False
    bestseller: bool = False
    new_arrival: bool = False
    bundle_eligible: bool = True
    status: Literal["active", "draft", "archived"] = "active"
    avg_rating: float = 0
    review_count: int = 0
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)


# ---------- Collections ----------
class Collection(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    slug: str
    description: str = ""
    image: Optional[str] = ""
    type: Literal["manual", "smart", "meal", "seasonal", "bundle", "homepage", "featured", "cuisine", "category"] = "manual"
    product_ids: List[str] = []
    rules: Optional[Dict[str, Any]] = None
    visible: bool = True
    sort_order: int = 0
    created_at: str = Field(default_factory=utcnow_iso)


class MealSlot(BaseModel):
    slot_key: str  # e.g. "rice_base"
    label: str
    required: bool = True
    default_product_ids: List[str] = []
    substitute_product_ids: List[str] = []
    quantity_hint: Optional[str] = None


class MealCollection(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    slug: str
    description: str = ""
    hero_image: Optional[str] = ""
    meal_tag: str  # jollof, pepper_soup, moi_moi, banga, efo_riro, breakfast
    user_intent_phrases: List[str] = []
    required_slots: List[MealSlot] = []
    optional_slots: List[MealSlot] = []
    protein_options: List[str] = []  # product_ids
    upsell_product_ids: List[str] = []
    recommended_bundle_id: Optional[str] = None
    tier: Literal["value", "standard", "premium", "family"] = "standard"
    servings_default: int = 4
    spice_level_default: str = "medium"
    active: bool = True
    visible: bool = True
    sort_order: int = 0
    created_at: str = Field(default_factory=utcnow_iso)


# ---------- Bundles ----------
class BundleItem(BaseModel):
    product_id: str
    quantity: int = 1
    required: bool = True


class Bundle(BaseModel):
    id: str = Field(default_factory=new_id)
    title: str
    slug: str
    description: str = ""
    image: Optional[str] = ""
    items: List[BundleItem] = []
    optional_items: List[BundleItem] = []
    price: float
    compare_at_price: Optional[float] = None
    discount_type: Literal["fixed", "percent", "none"] = "fixed"
    tier: Literal["standard", "family", "premium", "student"] = "standard"
    meal_tag: Optional[str] = None
    active: bool = True
    created_at: str = Field(default_factory=utcnow_iso)


# ---------- Cart / Orders ----------
class CartItem(BaseModel):
    product_id: str
    variant_sku: Optional[str] = None
    quantity: int = 1
    price: float = 0
    name: str = ""
    image: Optional[str] = ""
    size_label: Optional[str] = None


class Cart(BaseModel):
    id: str = Field(default_factory=new_id)
    customer_id: Optional[str] = None
    session_id: Optional[str] = None
    items: List[CartItem] = []
    coupon: Optional[str] = None
    notes: Optional[str] = ""
    updated_at: str = Field(default_factory=utcnow_iso)


class OrderAddress(BaseModel):
    name: str
    line1: str
    line2: Optional[str] = ""
    city: str = "Peterborough"
    postcode: str
    country: str = "UK"
    phone: Optional[str] = ""


class Order(BaseModel):
    id: str = Field(default_factory=new_id)
    order_number: str
    customer_id: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    items: List[CartItem] = []
    subtotal: float = 0
    delivery_fee: float = 0
    discount: float = 0
    total: float = 0
    currency: str = "gbp"
    address: Optional[OrderAddress] = None
    distance_miles: Optional[float] = None
    status: Literal["pending", "paid", "fulfilled", "shipped", "delivered", "cancelled", "refunded"] = "pending"
    payment_status: Literal["pending", "paid", "failed", "refunded"] = "pending"
    fulfillment_status: Literal["unfulfilled", "partial", "fulfilled"] = "unfulfilled"
    delivery_status: Literal["pending", "out_for_delivery", "delivered"] = "pending"
    stripe_session_id: Optional[str] = None
    notes: Optional[str] = ""
    timeline: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)


# ---------- AI Sessions ----------
class AIMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    created_at: str = Field(default_factory=utcnow_iso)
    basket: Optional[List[Dict[str, Any]]] = None


class AISession(BaseModel):
    id: str = Field(default_factory=new_id)
    customer_id: Optional[str] = None
    messages: List[AIMessage] = []
    last_basket: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=utcnow_iso)
    updated_at: str = Field(default_factory=utcnow_iso)


# ---------- Automations & Messaging ----------
class MessageTemplate(BaseModel):
    id: str = Field(default_factory=new_id)
    channel: Literal["email", "whatsapp", "sms"]
    name: str
    subject: Optional[str] = ""
    body: str
    variables: List[str] = []
    active: bool = True
    created_at: str = Field(default_factory=utcnow_iso)


class AutomationFlow(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str
    trigger: Literal[
        "order_placed", "order_shipped", "order_delivered",
        "abandoned_cart", "welcome", "replenishment", "back_in_stock",
        "meal_campaign", "review_request"
    ]
    channel: Literal["email", "whatsapp"]
    template_id: Optional[str] = None
    audience_segment: Optional[str] = "all"
    delay_minutes: int = 0
    active: bool = True
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    created_at: str = Field(default_factory=utcnow_iso)


# ---------- Audit ----------
class AuditLog(BaseModel):
    id: str = Field(default_factory=new_id)
    actor_email: Optional[str] = None
    actor_role: Optional[str] = None
    action: str  # e.g. "product.update"
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    ip: Optional[str] = None
    created_at: str = Field(default_factory=utcnow_iso)


# ---------- Wishlist & Saved Baskets ----------
class Wishlist(BaseModel):
    id: str = Field(default_factory=new_id)
    customer_id: str
    product_ids: List[str] = []
    updated_at: str = Field(default_factory=utcnow_iso)


# ---------- Reviews ----------
class Review(BaseModel):
    id: str = Field(default_factory=new_id)
    product_id: str
    customer_id: Optional[str] = None
    customer_name: str
    rating: int = 5
    title: str = ""
    body: str = ""
    verified: bool = True
    created_at: str = Field(default_factory=utcnow_iso)


# ---------- Delivery Zones ----------
class DeliveryZone(BaseModel):
    id: str = Field(default_factory=new_id)
    name: str = "Peterborough"
    address: str = "1227 Bourges Blvd, Peterborough PE1 2AU"
    radius_miles: float = 5
    per_mile_fee: float = 2.99
    free_threshold: float = 50
    active: bool = True


# ---------- Requests ----------
class CheckoutSessionBody(BaseModel):
    origin_url: str
    address: OrderAddress
    distance_miles: Optional[float] = 2.0
    notes: Optional[str] = ""
    coupon: Optional[str] = None


class CartAddBody(BaseModel):
    product_id: str
    variant_sku: Optional[str] = None
    quantity: int = 1


class AIAssistBody(BaseModel):
    session_id: Optional[str] = None
    message: str
    servings: Optional[int] = None
    spice_level: Optional[str] = None
    budget: Optional[str] = None
    protein: Optional[str] = None
