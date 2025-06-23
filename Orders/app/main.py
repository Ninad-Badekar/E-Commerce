# app/main.py
import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app.models import Base                       # Contains all models (Order, Inventory, Cart, etc.)
from app.carts.router import router as carts_router
from app.orders.router import router as orders_router 

# 1️⃣ Load environment variables (e.g. DATABASE_URL)
load_dotenv()

# 2️⃣ Create FastAPI instance with metadata
app = FastAPI(
    title="E-commerce Management API",
    version="1.0.0",
    description="Carts ↔ Orders",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 3️⃣ Enable CORS (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4️⃣ Create all tables in DB if not exists
Base.metadata.create_all(bind=engine)

# 5️⃣ Mount routers with prefixes and tags
app.include_router(carts_router, prefix="/carts", tags=["Carts"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
