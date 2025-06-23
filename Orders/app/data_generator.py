import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from sqlalchemy.orm import Session
from db import SessionLocal
from models import Product, Cart, CartItem, Order, OrderStatus

fake = Faker()

def utc_now():
    return datetime.now(timezone.utc)

def create_carts_and_items(db: Session, products, num_carts=200):
    carts = []
    for _ in range(num_carts):
        cart = Cart(
            customer_id=random.randint(1, 1000),
            created_at=utc_now()
        )
        db.add(cart)
        db.flush()  # Get cart_id

        num_items = random.randint(1, 5)
        used_product_ids = set()

        for _ in range(num_items):
            product = random.choice(products)
            if product.id in used_product_ids:
                continue
            used_product_ids.add(product.id)

            quantity = random.randint(1, 5)
            item = CartItem(
                cart_id=cart.cart_id,
                product_id=product.id,
                quantity=quantity
            )
            db.add(item)

        carts.append(cart)
    db.commit()
    print(f"Created {len(carts)} carts with items.")
    return carts

def create_orders_from_carts(db: Session, carts):
    order_count = 0
    for cart in carts:
        items = []
        total_amount = 0.0

        for item in cart.items:
            product = db.query(Product).filter_by(id=item.product_id).first()
            if not product:
                continue
            price = float(product.price)
            items.append({
                "product_id": product.id,
                "name": product.name,
                "qty": item.quantity,
                "price": price
            })
            total_amount += price * item.quantity

        if not items:
            continue

        order = Order(
            customer_id=cart.customer_id,
            order_date=utc_now(),
            items=items,
            total_amount=total_amount,
            status=OrderStatus.pending,
            payment_method=random.choice(["credit_card", "paypal", "stripe"]),
            shipping_address=fake.address()
        )
        db.add(order)
        order_count += 1

    db.commit()
    print(f"Created {order_count} orders from carts.")

def main():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        if not products:
            print("No products found. Run the product generator first.")
            return

        print("Generating carts and orders...")
        carts = create_carts_and_items(db, products, num_carts=200)
        create_orders_from_carts(db, carts)
        print("Done.")

    finally:
        db.close()

if __name__ == "__main__":
    main()
