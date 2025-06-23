from pydantic import BaseModel, Field, PositiveInt
from typing import List
from datetime import datetime

class Item(BaseModel):
    product_id: PositiveInt
    name: str = Field(..., min_length=2, max_length=100)
    quantity: int = PositiveInt
    price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_id: PositiveInt
    items: List[Item]
    payment_method: str = Field(..., min_length=3, max_length=225)
    shipping_address: str = Field(..., min_length=5, max_length=255)

class OrderResponse(BaseModel):
    order_id: PositiveInt
    order_date: datetime
    total_amount: float
    status: str

class OrderStatusUpdate(BaseModel):
    status: str = Field(..., min_length=1, max_length=50)

class CartItemResponse(BaseModel):
    product_id: PositiveInt
    name: str
    quantity: int
    price: float
