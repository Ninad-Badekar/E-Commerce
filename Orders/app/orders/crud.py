from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.orders import schemas  

def create_order(db: Session, order_in: schemas.OrderCreate) -> models.Order:
    total = sum(item.quantity * item.price for item in order_in.items)
    db_order = models.Order(
        user_id      = order_in.user_id,
        items            = [item.model_dump() for item in order_in.items],
        total_amount     = total,
        payment_method   = order_in.payment_method,
        shipping_address = order_in.shipping_address
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Finalize reserved stock
    try:
        reservations = [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in order_in.items
        ]
        finalize_reserved_products(reservations, order_id=str(db_order.id))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Order created but finalization failed: {str(e)}")

    return db_order


def get_order(db: Session, order_id: int) -> models.Order:
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order {order_id} not found")
    return order

def list_orders(db: Session):
    return db.query(models.Order).all()

def update_order_status(db: Session, order_id: int, status_str: str):
    order = get_order(db, order_id)
    try:
        order.status = models.OrderStatus(status_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid status: {status_str}")
    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if order.status == models.OrderStatus.canceled:  
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Order already cancelled")

    order.status = models.OrderStatus.canceled

    # Release reserved products
    try:
        reservations = [
            {"product_id": item.get("product_id"), "quantity": item.get("quantity", 0)}
            for item in order.items
        ]
        release_reserved_products(reservations, order_id=str(order.id))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Order cancelled but releasing reserved products failed: {str(e)}")

    db.commit()

import requests

def finalize_reserved_products(reservations: List[dict], order_id: str, base_url: str = "http://localhost:8000"):
    """
    Call the /products/finalize endpoint to mark reserved products as sold
    """
    url = f"{base_url}/products/finalize"
    payload = {
        "reservations": reservations,
        "order_id": order_id
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to finalize products: {response.json().get('detail')}")
    return response.json()

def release_reserved_products(reservations: List[dict], order_id: str, base_url: str = "http://localhost:8000"):
    """
    Call the /products/release endpoint to free up reserved products on cancellation
    """
    url = f"{base_url}/products/release"
    payload = {
        "reservations": reservations,
        "order_id": order_id
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to release products: {response.json().get('detail')}")
    return response.json()