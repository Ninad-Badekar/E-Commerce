from pydantic import BaseModel, PositiveInt
from typing import List, Optional
from datetime import datetime

# --- Cart Item Create ---
class CartItemCreate(BaseModel):
    product_id: PositiveInt
    quantity: PositiveInt

# --- Cart Item Response ---
class CartItemResponse(BaseModel):
    item_id: int
    product_id: int
    quantity: int
    remaining_available: Optional[int] = None  

    class Config:
        from_attributes = True

# --- Cart Create Request ---
class CartCreate(BaseModel):
    customer_id: PositiveInt

# --- Cart Full Response ---
class CartResponse(CartCreate):
    cart_id: int
    created_at: datetime
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True