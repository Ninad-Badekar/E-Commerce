from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models
from app.orders import schemas  

def create_order(db: Session, order_in: schemas.OrderCreate) -> models.Order:
    total = sum(item.quantity * item.price for item in order_in.items)
    db_order = models.Order(
        customer_id      = order_in.customer_id,
        items            = [item.model_dump() for item in order_in.items],
        total_amount     = total,
        payment_method   = order_in.payment_method,
        shipping_address = order_in.shipping_address
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
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
    if order.status == models.OrderStatus.canceled:  # use exact enum member name here
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Order already cancelled")

    order.status = models.OrderStatus.canceled

    for item in order.items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 0)
        if product_id and quantity:
            inv = db.query(models.Inventory).filter_by(product_id=product_id).first()
            if inv:
                inv.stock += quantity

    db.commit()
