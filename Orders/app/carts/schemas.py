from pydantic import BaseModel, PositiveInt
from typing import List
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: PositiveInt
    quantity: PositiveInt

class CartItemResponse(BaseModel):
    item_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode

class CartCreate(BaseModel):
    customer_id: PositiveInt

class CartResponse(CartCreate):
    cart_id: int
    created_at: datetime
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True  # Pydantic v2 replacement for orm_mode
