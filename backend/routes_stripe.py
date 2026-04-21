"""Stripe Checkout routes."""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Header, Depends
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest,
)
from db import carts, orders, products, payment_transactions, customers
from models import CheckoutSessionBody, new_id, utcnow_iso
from auth import get_current_user

load_dotenv()

router = APIRouter(prefix="/api")

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")


def _compute_delivery_fee(subtotal: float, distance_miles: float) -> tuple[float, bool, str]:
    per_mile = float(os.environ.get("DELIVERY_PER_MILE", 2.99))
    free_threshold = float(os.environ.get("FREE_DELIVERY_THRESHOLD", 50))
    radius = float(os.environ.get("DELIVERY_RADIUS_MILES", 5))
    if distance_miles > radius:
        return 0, False, f"Outside {radius}-mile delivery radius"
    if subtotal >= free_threshold:
        return 0, True, "Free delivery (order over £50)"
    fee = round(per_mile * max(distance_miles, 0), 2)
    return fee, True, f"{distance_miles} miles × £{per_mile}/mile"


def _gen_order_number():
    return "AFB-" + new_id()[:8].upper()


@router.post("/checkout/session")
async def create_checkout_session(
    body: CheckoutSessionBody,
    request: Request,
    session_id: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    payload = await get_current_user(authorization)
    customer_id = payload["sub"] if payload and payload.get("type") == "customer" else None
    customer_email = payload.get("email") if payload and payload.get("type") == "customer" else None

    # Fetch cart
    q = {"customer_id": customer_id} if customer_id else {"session_id": session_id}
    cart = await carts.find_one(q, {"_id": 0})
    if not cart or not cart["items"]:
        raise HTTPException(400, "Cart is empty")

    subtotal = round(sum(i["price"] * i["quantity"] for i in cart["items"]), 2)
    fee, available, reason = _compute_delivery_fee(subtotal, body.distance_miles or 2.0)
    if not available:
        raise HTTPException(400, reason)
    total = round(subtotal + fee, 2)

    order_number = _gen_order_number()

    origin = body.origin_url.rstrip("/")
    success_url = f"{origin}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}&order={order_number}"
    cancel_url = f"{origin}/cart"

    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{str(request.base_url).rstrip('/')}/api/webhook/stripe")

    metadata = {
        "order_number": order_number,
        "customer_id": customer_id or "guest",
        "customer_email": customer_email or body.address.name,
    }
    checkout_req = CheckoutSessionRequest(
        amount=float(total), currency="gbp",
        success_url=success_url, cancel_url=cancel_url, metadata=metadata,
    )
    session = await stripe_checkout.create_checkout_session(checkout_req)

    # Create pending order
    order_doc = {
        "id": new_id(),
        "order_number": order_number,
        "customer_id": customer_id, "customer_email": customer_email or None,
        "items": list(cart["items"]),
        "subtotal": subtotal, "delivery_fee": fee, "discount": 0, "total": total,
        "currency": "gbp",
        "address": body.address.model_dump(),
        "distance_miles": body.distance_miles,
        "status": "pending", "payment_status": "pending",
        "fulfillment_status": "unfulfilled", "delivery_status": "pending",
        "stripe_session_id": session.session_id,
        "notes": body.notes or "",
        "timeline": [{"at": utcnow_iso(), "by": "system", "change": {"created": True}}],
        "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
    }
    await orders.insert_one(order_doc)

    # Create payment transaction
    await payment_transactions.insert_one({
        "id": new_id(),
        "session_id": session.session_id, "order_number": order_number,
        "amount": total, "currency": "gbp",
        "customer_id": customer_id, "customer_email": customer_email,
        "payment_status": "initiated", "status": "pending",
        "metadata": metadata,
        "created_at": utcnow_iso(), "updated_at": utcnow_iso(),
    })

    return {"url": session.url, "session_id": session.session_id,
            "order_number": order_number, "total": total, "delivery_fee": fee,
            "subtotal": subtotal}


@router.get("/checkout/status/{session_id}")
async def check_status(session_id: str, request: Request):
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{str(request.base_url).rstrip('/')}/api/webhook/stripe")
    status = await stripe_checkout.get_checkout_status(session_id)
    txn = await payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(404, "Transaction not found")

    # Idempotent update
    if txn.get("payment_status") != "paid" and status.payment_status == "paid":
        await payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "paid", "status": status.status, "updated_at": utcnow_iso()}},
        )
        order_number = (status.metadata or {}).get("order_number") or txn.get("order_number")
        if order_number:
            o = await orders.find_one({"order_number": order_number}, {"_id": 0})
            if o and o.get("payment_status") != "paid":
                await orders.update_one(
                    {"order_number": order_number},
                    {"$set": {"payment_status": "paid", "status": "paid", "updated_at": utcnow_iso()},
                     "$push": {"timeline": {"at": utcnow_iso(), "by": "stripe", "change": {"payment_status": "paid"}}}},
                )
                # Update customer totals
                if o.get("customer_id"):
                    await customers.update_one({"id": o["customer_id"]}, {
                        "$inc": {"total_spend": o["total"], "order_count": 1}
                    })
                # Decrement inventory
                for it in o["items"]:
                    await products.update_one({"id": it["product_id"]}, {"$inc": {"stock": -int(it["quantity"])}})
                # Clear cart
                q = {"customer_id": o["customer_id"]} if o.get("customer_id") else None
                if q:
                    await carts.update_one(q, {"$set": {"items": [], "updated_at": utcnow_iso()}})
    elif status.payment_status != "paid" and status.status == "expired":
        await payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "expired", "updated_at": utcnow_iso()}},
        )

    # Return fresh data
    txn = await payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency,
        "metadata": status.metadata,
        "transaction": txn,
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{str(request.base_url).rstrip('/')}/api/webhook/stripe")
    try:
        event = await stripe_checkout.handle_webhook(payload, sig)
    except Exception as e:
        raise HTTPException(400, f"Invalid webhook: {str(e)[:100]}")

    if event.payment_status == "paid":
        txn = await payment_transactions.find_one({"session_id": event.session_id}, {"_id": 0})
        if txn and txn.get("payment_status") != "paid":
            await payment_transactions.update_one(
                {"session_id": event.session_id},
                {"$set": {"payment_status": "paid", "status": "complete", "updated_at": utcnow_iso()}},
            )
            order_number = (event.metadata or {}).get("order_number") or txn.get("order_number")
            if order_number:
                o = await orders.find_one({"order_number": order_number}, {"_id": 0})
                if o and o.get("payment_status") != "paid":
                    await orders.update_one(
                        {"order_number": order_number},
                        {"$set": {"payment_status": "paid", "status": "paid", "updated_at": utcnow_iso()},
                         "$push": {"timeline": {"at": utcnow_iso(), "by": "stripe_webhook", "change": {"payment_status": "paid"}}}},
                    )
                    if o.get("customer_id"):
                        await customers.update_one({"id": o["customer_id"]}, {
                            "$inc": {"total_spend": o["total"], "order_count": 1}
                        })
                    for it in o["items"]:
                        await products.update_one({"id": it["product_id"]}, {"$inc": {"stock": -int(it["quantity"])}})
    return {"received": True}
