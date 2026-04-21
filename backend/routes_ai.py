"""AI Meal Assistant route - GPT-5.2 via Emergent LLM key."""
import os
import json
import re
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from emergentintegrations.llm.chat import LlmChat, UserMessage

from db import ai_sessions, products, meal_collections, clean
from models import new_id, utcnow_iso, AIAssistBody
from auth import get_current_user

load_dotenv()

router = APIRouter(prefix="/api/ai")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


SYSTEM_PROMPT = """You are Afrobean AI — the friendly, expert meal assistant for Afrobean, a premium African online supermarket in Peterborough, UK (currency £).

Your job: help shoppers figure out what to cook and build their basket. Focus on authentic African dishes (Nigerian, West African, pan-African).

You have a catalogue of real products (rice, flours, swallows, oils, spices, soup bases, breakfast, snacks, drinks, frozen fish/meat, beauty, household). You will be told meal collections + mapping slots the user can choose from.

CONVERSATION STYLE:
- Warm, concise, encouraging. Use British English.
- Prefer short paragraphs + short bullet lists.
- When a user asks to cook something, ask brief follow-ups if you need: servings, protein preference, spice level, budget or premium preference. Never ask more than 2 follow-ups at a time.
- If the user is explicit (e.g. "jollof for 5"), skip questions and build the basket.
- Always mention free delivery over £50 when relevant.

OUTPUT FORMAT:
When you have enough info to recommend a basket, output a JSON block surrounded by <basket>...</basket>. Inside the tags output a valid JSON object with this shape:
{
  "meal": "jollof rice",
  "servings": 5,
  "items": [
    {"product_id": "<id>", "name": "<name>", "quantity": 1, "reason": "<why>"}
  ],
  "notes": "short tip or upsell message",
  "upsells": [{"product_id": "<id>", "name": "<name>"}]
}

Prefer in-stock items. Suggest family or bulk sizes for bigger servings. Always include every required slot for the detected meal.
Outside the <basket>...</basket> block, write a warm human response.
If the user is just browsing or greeting, respond warmly and suggest 2-3 meals they could try. Do not emit a basket in that case.
"""


async def _build_catalog_context() -> str:
    """Build a compact catalog snippet to feed the model."""
    # Only include products with meal_tags or ai_meal_roles
    items = []
    async for p in products.find(
        {"status": "active", "$or": [{"meal_tags": {"$ne": []}}, {"ai_meal_roles": {"$ne": []}}]},
        {"_id": 0, "id": 1, "name": 1, "price": 1, "stock": 1, "meal_tags": 1, "ai_meal_roles": 1, "brand": 1}
    ).limit(120):
        items.append(f"- {p['id']} | {p['name']} | £{p['price']} | stock:{p['stock']} | meals:{','.join(p.get('meal_tags', []))} | roles:{','.join(p.get('ai_meal_roles', []))}")
    # Meal collections
    mc_list = []
    async for mc in meal_collections.find({}, {"_id": 0, "title": 1, "meal_tag": 1, "user_intent_phrases": 1}):
        mc_list.append(f"- {mc['meal_tag']}: {mc['title']} (intents: {', '.join(mc.get('user_intent_phrases', [])[:4])})")
    return f"CATALOGUE (product_id | name | price | stock | meals | roles):\n" + "\n".join(items) + f"\n\nMEAL COLLECTIONS:\n" + "\n".join(mc_list)


def _extract_basket(text: str):
    m = re.search(r"<basket>(.*?)</basket>", text, re.DOTALL | re.IGNORECASE)
    if not m:
        return None, text
    inner = m.group(1).strip()
    try:
        basket = json.loads(inner)
    except Exception:
        return None, text
    # Strip tags from text shown to user
    cleaned = (text[:m.start()] + text[m.end():]).strip()
    return basket, cleaned


@router.post("/chat")
async def ai_chat(body: AIAssistBody, authorization: Optional[str] = Header(None)):
    payload = await get_current_user(authorization)
    customer_id = payload["sub"] if payload and payload.get("type") == "customer" else None

    session_id = body.session_id or new_id()
    session = await ai_sessions.find_one({"id": session_id}, {"_id": 0})
    if not session:
        session = {"id": session_id, "customer_id": customer_id, "messages": [],
                   "last_basket": [], "created_at": utcnow_iso(), "updated_at": utcnow_iso()}
        await ai_sessions.insert_one(session)
        session = {k: v for k, v in session.items() if k != "_id"}

    # Build catalog context once per session call
    catalog_ctx = await _build_catalog_context()

    system_message = SYSTEM_PROMPT + "\n\n" + catalog_ctx

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message,
    ).with_model("openai", "gpt-5.2")

    # Replay prior messages (LlmChat maintains its own mem via session_id; to be safe, we include user turn only)
    user_text = body.message
    if body.servings or body.spice_level or body.budget or body.protein:
        context_bits = []
        if body.servings: context_bits.append(f"servings={body.servings}")
        if body.spice_level: context_bits.append(f"spice_level={body.spice_level}")
        if body.budget: context_bits.append(f"budget={body.budget}")
        if body.protein: context_bits.append(f"protein={body.protein}")
        user_text = f"{user_text}\n\n(user preferences: {', '.join(context_bits)})"

    try:
        response_text = await chat.send_message(UserMessage(text=user_text))
    except Exception as e:
        raise HTTPException(500, f"AI service error: {str(e)[:200]}")

    basket, visible_text = _extract_basket(response_text)

    # If basket present, hydrate products
    hydrated_items = []
    if basket and isinstance(basket, dict):
        for it in basket.get("items", []) or []:
            pid = it.get("product_id")
            p = await products.find_one({"id": pid, "status": "active"}, {"_id": 0})
            if p:
                hydrated_items.append({
                    "product_id": pid, "name": p["name"],
                    "image": p["images"][0] if p.get("images") else None,
                    "price": p["price"], "quantity": int(it.get("quantity", 1)),
                    "reason": it.get("reason", ""), "variant_sku": None,
                })
        basket["hydrated_items"] = hydrated_items

    # Save turn to session
    session["messages"].append({"role": "user", "content": body.message, "created_at": utcnow_iso()})
    session["messages"].append({"role": "assistant", "content": visible_text, "created_at": utcnow_iso(), "basket": basket})
    if basket:
        session["last_basket"] = hydrated_items
    await ai_sessions.update_one({"id": session_id},
                                 {"$set": {"messages": session["messages"],
                                           "last_basket": session.get("last_basket", []),
                                           "updated_at": utcnow_iso()}})
    return {
        "session_id": session_id,
        "reply": visible_text,
        "basket": basket,
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    s = await ai_sessions.find_one({"id": session_id}, {"_id": 0})
    if not s:
        raise HTTPException(404)
    return s


@router.post("/sessions/{session_id}/add-to-cart")
async def add_basket_to_cart(session_id: str, data: Dict[str, Any] = None,
                             session_qs: Optional[str] = None, authorization: Optional[str] = Header(None)):
    """Push last basket items to the user's cart."""
    from routes_shop import _get_or_create_cart
    from db import carts
    s = await ai_sessions.find_one({"id": session_id}, {"_id": 0})
    if not s or not s.get("last_basket"):
        raise HTTPException(404, "No basket to add")
    payload = await get_current_user(authorization)
    cid = payload["sub"] if payload and payload.get("type") == "customer" else None
    cart_session_id = (data or {}).get("cart_session_id") or new_id()
    cart = await _get_or_create_cart(cid, cart_session_id)
    for it in s["last_basket"]:
        pid = it["product_id"]
        qty = it.get("quantity", 1)
        p = await products.find_one({"id": pid, "status": "active"}, {"_id": 0})
        if not p:
            continue
        variant = next((v for v in p["variants"] if v.get("is_default")), p["variants"][0] if p["variants"] else None)
        existing = next((c for c in cart["items"] if c["product_id"] == pid), None)
        if existing:
            existing["quantity"] += qty
        else:
            cart["items"].append({
                "product_id": pid,
                "variant_sku": variant["sku"] if variant else None,
                "quantity": qty, "price": variant["price"] if variant else p["price"],
                "name": p["name"], "image": p["images"][0] if p.get("images") else None,
                "size_label": variant["size_label"] if variant else None,
            })
    await carts.update_one({"id": cart["id"]}, {"$set": {"items": cart["items"], "updated_at": utcnow_iso()}})
    return {"ok": True, "cart_id": cart["id"], "session_id": cart.get("session_id")}
