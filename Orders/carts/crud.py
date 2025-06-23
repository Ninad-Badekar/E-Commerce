from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models import Cart, CartItem, Inventory
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

def add_item(db: Session, cart_id: int, item_in: CartItemCreate) -> CartItem:
    inv = db.query(Inventory).filter_by(product_id=item_in.product_id).first()
    if not inv or inv.stock < item_in.quantity:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient stock")

    item = db.query(CartItem).filter_by(cart_id=cart_id, product_id=item_in.product_id).first()
    if item:
        new_quantity = item.quantity + item_in.quantity
        if inv.stock < new_quantity:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not enough stock to increase quantity")
        item.quantity = new_quantity
    else:
        item = CartItem(cart_id=cart_id, **item_in.dict())
        db.add(item)

    inv.stock -= item_in.quantity
    db.commit()
    db.refresh(item)
    return item

def list_cart_items(db: Session, cart_id: int):
    cart = get_cart(db, cart_id)
    return cart.items

def update_item_quantity(db: Session, cart_id: int, product_id: int, quantity: int):
    item = db.query(CartItem).filter_by(cart_id=cart_id, product_id=product_id).first()
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found in cart")

    inv = db.query(Inventory).filter_by(product_id=product_id).first()
    if not inv or inv.stock + item.quantity < quantity:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient stock to update")

    inv.stock += item.quantity  # Restore old stock
    item.quantity = quantity
    inv.stock -= quantity       # Deduct new quantity

    db.commit()
    db.refresh(item)
    return item

def remove_item(db: Session, item_id: int):
    item = db.query(CartItem).filter_by(item_id=item_id).first()
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cart item not found")

    inv = db.query(Inventory).filter_by(product_id=item.product_id).first()
    if inv:
        inv.stock += item.quantity
    db.delete(item)
    db.commit()

def clear_cart(db: Session, cart_id: int):
    items = db.query(CartItem).filter_by(cart_id=cart_id).all()
    for item in items:
        inv = db.query(Inventory).filter_by(product_id=item.product_id).first()
        inv.stock += item.quantity
        db.delete(item)
    db.commit()