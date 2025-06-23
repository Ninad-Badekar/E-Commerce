from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Cart, CartItem
from app.carts.schemas import CartCreate, CartItemCreate

def create_cart(db: Session, cart_in: CartCreate) -> Cart:
    cart = Cart(customer_id=cart_in.customer_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def get_cart(db: Session, cart_id: int) -> Cart:
    cart = db.query(Cart).filter_by(cart_id=cart_id).first()
    if not cart:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Cart {cart_id} not found")
    return cart

from Products.routers.product_router import reserve_products
from fastapi import Request

def add_item(db: Session, cart_id: int, item_in: CartItemCreate) -> CartItem:
    # Reserve product
    reserve_products(
        reservations={"product_id": item_in.product_id, "quantity": item_in.quantity},
        order_id=f"cart_{cart_id}",
        db=db
    )

    item = db.query(CartItem).filter_by(cart_id=cart_id, product_id=item_in.product_id).first()
    if item:
        item.quantity += item_in.quantity
    else:
        item = CartItem(cart_id=cart_id, **item_in.dict())
        db.add(item)

    db.commit()
    db.refresh(item)
    return item


def list_cart_items(db: Session, cart_id: int):
    cart = get_cart(db, cart_id)
    return cart.items

from Products.routers.product_router import reserve_products, release_products

def update_item_quantity(db: Session, cart_id: int, product_id: int, quantity: int):
    item = db.query(CartItem).filter_by(cart_id=cart_id, product_id=product_id).first()
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found in cart")

    quantity_diff = quantity - item.quantity
    if quantity_diff > 0:
        # Increase reserve
        reserve_products(
            reservations={"product_id": product_id, "quantity": quantity_diff},
            order_id=f"cart_{cart_id}",
            db=db
        )
    elif quantity_diff < 0:
        # Release reserve
        release_products(
            reservations={"product_id": product_id, "quantity": abs(quantity_diff)},
            order_id=f"cart_{cart_id}",
            db=db
        )

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_item(db: Session, item_id: int):
    item = db.query(CartItem).filter_by(item_id=item_id).first()
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cart item not found")

    # Use your product release endpoint logic
    release_products(
        reservations={"product_id": item.product_id, "quantity": item.quantity},
        order_id=f"cart_{item.cart_id}",
        db=db
    )

    db.delete(item)
    db.commit()

def clear_cart(db: Session, cart_id: int):
    items = db.query(CartItem).filter_by(cart_id=cart_id).all()
    for item in items:
        release_products(
            reservations={"product_id": item.product_id, "quantity": item.quantity},
            order_id=f"cart_{cart_id}",
            db=db
        )
        db.delete(item)
    db.commit()