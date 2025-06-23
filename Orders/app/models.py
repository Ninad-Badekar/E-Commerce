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
# Utility Function
# ─────────────────────────────────────────────────────
def utc_now():
    return datetime.now(timezone.utc)

# ─────────────────────────────────────────────────────
#  Cart & Cart Items
# ─────────────────────────────────────────────────────
class Cart(Base):
    __tablename__ = "carts"

    cart_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
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
#  Order & Order Status
# ─────────────────────────────────────────────────────
class OrderStatus(enum.Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    order_date = Column(DateTime, default=utc_now, nullable=False)
    items = Column(JSON, nullable=False)  # Serialized list of order items
    total_amount = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    payment_method = Column(String(50), nullable=True)
    shipping_address = Column(String(255), nullable=False)