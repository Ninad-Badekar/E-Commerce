# # data_generator.py
# import random
# from datetime import datetime, timedelta, timezone
# from decimal import Decimal
# from faker import Faker
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

# from models import (
#     Base, Category, Product, Inventory, PriceHistory,
#     StockMovement, Cart, CartItem, Order, OrderStatus
# )
# from db import DATABASE_URL  # Adjust according to your project

# fake = Faker()
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)

# def utc_now():
#     return datetime.now(timezone.utc)

# def create_categories(db: Session, n=5):
#     categories = []
#     for _ in range(n):
#         category = Category(
#             name=fake.unique.word(),
#             created_at=utc_now(),
#             updated_at=utc_now()
#         )
#         db.add(category)
#         categories.append(category)
#     db.commit()
#     return categories

# def create_products(db: Session, categories, n=20):
#     products = []
#     for _ in range(n):
#         category = random.choice(categories)
#         price = round(random.uniform(10, 1000), 2)
#         product = Product(
#             name=fake.unique.word().title(),
#             price=price,
#             brand=fake.company(),
#             attributes={"color": fake.color_name(), "size": random.choice(["S", "M", "L", "XL"])},
#             category=category,
#             created_at=utc_now(),
#             updated_at=utc_now(),
#         )
#         db.add(product)
#         products.append(product)
#     db.commit()
#     return products

# def create_inventory(db: Session, products):
#     for product in products:
#         stock = random.randint(0, 100)
#         inv = Inventory(
#             product_id=product.id,
#             stock=stock,
#             quantity_reserve=random.randint(0, stock//2),
#             reorder_level=10,
#             reorder_quantity=20,
#             unit_cost=round(random.uniform(5, 500), 2),
#             last_restocked=utc_now() - timedelta(days=random.randint(0, 30)),
#             expiry_date=utc_now() + timedelta(days=random.randint(30, 365)),
#             batch_number=fake.bothify(text='??####'),
#             location=fake.city(),
#             last_updated=utc_now()
#         )
#         db.add(inv)
#     db.commit()
# def create_price_history(db: Session, products):
#     for product in products:
#         multiplier = Decimal(str(random.uniform(0.8, 1.2)))
#         old_price = (product.price * multiplier).quantize(Decimal("0.01"))
#         new_price = product.price
#         ph = PriceHistory(
#             product_id=product.id,
#             old_price=old_price,
#             new_price=new_price,
#             changed_at=utc_now() - timedelta(days=random.randint(1, 30)),
#             reason=fake.sentence(nb_words=6)
#         )
#         db.add(ph)
#     db.commit()

# def create_stock_movements(db: Session, products):
#     reasons = ["Initial stock", "Restock", "Sale", "Return"]
#     for product in products:
#         for _ in range(random.randint(1, 5)):
#             change = random.randint(-20, 50)
#             sm = StockMovement(
#                 product_id=product.id,
#                 change=change,
#                 reason=random.choice(reasons),
#                 timestamp=utc_now() - timedelta(days=random.randint(0, 60))
#             )
#             db.add(sm)
#     db.commit()

# def create_carts_and_items(db: Session, products, n=5):
#     carts = []
#     for _ in range(n):
#         cart = Cart(
#             customer_id=random.randint(1, 1000),
#             created_at=utc_now()
#         )
#         db.add(cart)
#         db.flush()  # to get cart_id

#         n_items = random.randint(1, 5)
#         for _ in range(n_items):
#             product = random.choice(products)
#             quantity = random.randint(1, 5)
#             if product.inventory and product.inventory.stock >= quantity:
#                 item = CartItem(
#                     cart_id=cart.cart_id,
#                     product_id=product.id,
#                     quantity=quantity
#                 )
#                 db.add(item)
#         carts.append(cart)
#     db.commit()
#     return carts

# def create_orders(db: Session, carts):
#     for cart in carts:
#         items = []
#         total_amount = 0.0
#         for item in cart.items:
#             product = db.get(Product, item.product_id)
#             if not product:
#                 continue
#             price = float(product.price)
#             items.append({
#                 "product_id": product.id,
#                 "name": product.name,
#                 "qty": item.quantity,
#                 "price": price,
#             })
#             total_amount += price * item.quantity

#         if not items:
#             continue

#         order = Order(
#             customer_id=cart.customer_id,
#             order_date=utc_now(),
#             items=items,
#             total_amount=total_amount,
#             status=OrderStatus.pending,
#             payment_method=random.choice(["credit_card", "paypal", "stripe"]),
#             shipping_address=fake.address(),
#         )
#         db.add(order)
#     db.commit()

# def main():
#     Base.metadata.create_all(bind=engine)
#     db = SessionLocal()

#     try:
#         print("Creating categories...")
#         categories = create_categories(db)

#         print("Creating products...")
#         products = create_products(db, categories)

#         print("Creating inventory for products...")
#         create_inventory(db, products)

#         print("Creating price histories...")
#         create_price_history(db, products)

#         print("Creating stock movements...")
#         create_stock_movements(db, products)

#         print("Creating carts and cart items...")
#         carts = create_carts_and_items(db, products)

#         print("Creating orders from carts...")
#         create_orders(db, carts)

#         print("Data generation complete!")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     main()
# data_generator.py
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from faker import Faker
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Base, Category, Product, Inventory, PriceHistory,
    StockMovement, Cart, CartItem, Order, OrderStatus
)
from db import DATABASE_URL  # Adjust this if needed

fake = Faker()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def utc_now():
    return datetime.now(timezone.utc)

def create_categories(db: Session, n=5):
    categories = []
    for _ in range(n):
        category = Category(
            name=fake.unique.word(),
            created_at=utc_now(),
            updated_at=utc_now()
        )
        db.add(category)
        categories.append(category)
    db.commit()
    return categories

def create_products(db: Session, categories, n=20):
    products = []
    for _ in range(n):
        category = random.choice(categories)
        price = round(random.uniform(10, 1000), 2)
        product = Product(
            name=fake.unique.word().title(),
            price=price,
            brand=fake.company(),
            attributes={
                "color": fake.color_name(),
                "size": random.choice(["S", "M", "L", "XL"])
            },
            category=category,
            created_at=utc_now(),
            updated_at=utc_now()
        )
        db.add(product)
        products.append(product)
    db.commit()
    return products

def create_inventory(db: Session, products):
    for product in products:
        stock = random.randint(0, 100)
        inv = Inventory(
            product_id=product.id,
            stock=stock,
            quantity_reserve=random.randint(0, stock // 2 if stock > 1 else 0),
            reorder_level=10,
            reorder_quantity=20,
            unit_cost=round(random.uniform(5, 500), 2),
            last_restocked=utc_now() - timedelta(days=random.randint(0, 30)),
            expiry_date=utc_now() + timedelta(days=random.randint(30, 365)),
            batch_number=fake.bothify(text='??####'),
            location=fake.city(),
            last_updated=utc_now()
        )
        db.add(inv)
    db.commit()

def create_price_history(db: Session, products):
    for product in products:
        multiplier = Decimal(str(random.uniform(0.8, 1.2)))
        old_price = (Decimal(product.price) * multiplier).quantize(Decimal("0.01"))
        new_price = Decimal(product.price).quantize(Decimal("0.01"))
        ph = PriceHistory(
            product_id=product.id,
            old_price=old_price,
            new_price=new_price,
            changed_at=utc_now() - timedelta(days=random.randint(1, 30)),
            reason=fake.sentence(nb_words=6)
        )
        db.add(ph)
    db.commit()

def create_stock_movements(db: Session, products):
    reasons = ["Initial stock", "Restock", "Sale", "Return"]
    for product in products:
        for _ in range(random.randint(1, 5)):
            change = random.randint(-20, 50)
            sm = StockMovement(
                product_id=product.id,
                change=change,
                reason=random.choice(reasons),
                timestamp=utc_now() - timedelta(days=random.randint(0, 60))
            )
            db.add(sm)
    db.commit()

def create_carts_and_items(db: Session, products, n=5):
    carts = []
    for _ in range(n):
        cart = Cart(
            customer_id=random.randint(1, 1000),
            created_at=utc_now()
        )
        db.add(cart)
        db.flush()  # Get cart_id

        n_items = random.randint(1, 5)
        used_products = set()

        for _ in range(n_items):
            product = random.choice(products)
            if product.id in used_products:
                continue  # Avoid duplicate product in one cart
            used_products.add(product.id)

            quantity = random.randint(1, 5)
            if product.inventory and product.inventory.stock >= quantity:
                item = CartItem(
                    cart_id=cart.cart_id,
                    product_id=product.id,
                    quantity=quantity
                )
                db.add(item)
        carts.append(cart)
    db.commit()
    return carts

def create_orders(db: Session, carts):
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
    db.commit()

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Creating categories...")
        categories = create_categories(db)

        print("Creating products...")
        products = create_products(db, categories)

        print("Creating inventory for products...")
        create_inventory(db, products)

        print("Creating price histories...")
        create_price_history(db, products)

        print("Creating stock movements...")
        create_stock_movements(db, products)

        print("Creating carts and cart items...")
        carts = create_carts_and_items(db, products)

        print("Creating orders from carts...")
        create_orders(db, carts)

        print("✅ Data generation complete!")
    finally:
        db.close()

if __name__ == "__main__":
    main()