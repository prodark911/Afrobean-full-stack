"""Afrobean main FastAPI server."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from db import ensure_indexes
from routes_catalog import router as catalog_router
from routes_shop import router as shop_router
from routes_admin import router as admin_router
from routes_ai import router as ai_router
from routes_stripe import router as stripe_router
from seed import seed_all

app = FastAPI(title="Afrobean API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def root():
    return {"service": "afrobean-api", "status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/store-info")
async def store_info():
    return {
        "name": "Afrobean",
        "tagline": "Peterborough's premium African food supermarket",
        "address": os.environ.get("STORE_ADDRESS", "1227 Bourges Blvd, Peterborough PE1 2AU"),
        "free_delivery_threshold": float(os.environ.get("FREE_DELIVERY_THRESHOLD", 50)),
        "delivery_per_mile": float(os.environ.get("DELIVERY_PER_MILE", 2.99)),
        "delivery_radius_miles": float(os.environ.get("DELIVERY_RADIUS_MILES", 5)),
        "currency": "GBP",
        "whatsapp_phone": "+44 7700 900123",
    }


app.include_router(catalog_router)
app.include_router(shop_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(stripe_router)


@app.on_event("startup")
async def on_startup():
    await ensure_indexes()
    await seed_all()
