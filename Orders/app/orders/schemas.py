from pydantic import BaseModel, Field, PositiveInt
from typing import List
from datetime import datetime


# --- Item schema used for creating an order ---
class Item(BaseModel):
    product_id: PositiveInt
    name: str = Field(..., min_length=2, max_length=100)
    quantity: int = PositiveInt
    price: float = Field(..., gt=0)


# --- Used when creating an order ---
class OrderCreate(BaseModel):
    user_id: PositiveInt
    items: List[Item]
    payment_method: str = Field(..., min_length=3, max_length=225)
    shipping_address: str = Field(..., min_length=5, max_length=255)


# --- Response model for each item inside OrderResponse ---
class OrderItemResponse(BaseModel):
    product_id: PositiveInt
    name: str
    quantity: int
    price: float


# --- Response model for an order ---
class OrderResponse(BaseModel):
    order_id: PositiveInt
    order_date: datetime
    total_amount: float
    status: str
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2


# --- Used to update order status (PATCH endpoint) ---
class OrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)


# --- Optional: used in cancel_order endpoint response ---
class OrderCancelResponse(BaseModel):
    detail: str


# --- This seems related to the cart, not orders ---
class CartItemResponse(BaseModel):
    product_id: PositiveInt
    name: str
    quantity: int
    price: float