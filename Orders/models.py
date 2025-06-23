import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum,
    JSON, Numeric
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# ─────────────────────────────────────────────────────
# 🕒 Utility Function
# ─────────────────────────────────────────────────────
def utc_now():
    return datetime.now(timezone.utc)

# ─────────────────────────────────────────────────────
# 📦 Product & Category Models
# ─────────────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False, index=True)
    brand = Column(String(100), index=True)
    attributes = Column(JSON, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

# ─────────────────────────────────────────────────────
# 📊 Inventory & Stock Tracking
# ─────────────────────────────────────────────────────
class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True, unique=True)
    stock = Column(Integer, default=0, nullable=False)
    quantity_reserve = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=20)
    unit_cost = Column(Numeric(10, 2), nullable=True)
    last_restocked = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    batch_number = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=utc_now, onupdate=utc_now)

    product = relationship("Product", back_populates="inventory")


class PriceHistory(Base):
    __tablename__ = "product_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    old_price = Column(Numeric(10, 2), nullable=False)
    new_price = Column(Numeric(10, 2), nullable=False)
    changed_at = Column(DateTime, default=utc_now)
    reason = Column(String(100), nullable=True)

    product = relationship("Product", back_populates="price_history")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    change = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    product = relationship("Product", back_populates="stock_movements")

# ─────────────────────────────────────────────────────
# 🛒 Cart & Cart Items
# ─────────────────────────────────────────────────────
class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.cart_id", ondelete="CASCADE"))
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    cart = relationship("Cart", back_populates="items")

# ─────────────────────────────────────────────────────
# 📦 Order & Order Status
# ─────────────────────────────────────────────────────
class OrderStatus(enum.Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False, index=True)
    order_date = Column(DateTime, default=utc_now, nullable=False)
    items = Column(JSON, nullable=False)  # Serialized list of order items
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    payment_method = Column(String(50), nullable=True)
    shipping_address = Column(String(255), nullable=False)
