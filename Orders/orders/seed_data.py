from faker import Faker
from pydantic import ValidationError
import random

from db import engine, SessionLocal
from models import Base
from crud import create_order
from schemas import OrderCreate, Item

# 1) Ensure tables exist
Base.metadata.create_all(bind=engine)

faker = Faker()
db = SessionLocal()
DATA_SIZE = 50

def main():
    seeded = 0

    for _ in range(DATA_SIZE):
        # 2) Build a random list of items, with integer product_ids
        raw_items = []
        for __ in range(faker.random_int(min=1, max=4)):
            raw_items.append({
                "product_id": faker.random_int(min=1, max=1000),
                "name": faker.pystr(min_chars=2, max_chars=100),
                "quantity": faker.random_int(min=1, max=5),
                "price": round(faker.random_number(digits=3) + faker.random.random(), 2),
            })

        try:
            # 3) Validate items via Pydantic
            items = [Item(**it) for it in raw_items]

            # 4) Build your OrderCreate with integer customer_id
            order_in = OrderCreate(
                customer_id=faker.random_int(min=1, max=500),
                items=items,
                payment_method=random.choice(["credit_card", "paypal", "upi"]),
                shipping_address=faker.address(),
            )

            # 5) Persist to the DB
            create_order(db, order_in)
            seeded += 1

        except ValidationError as ve:
            print("ValidationError—skipping this order:", ve)
            continue

    print(f"Seeded {seeded}/{DATA_SIZE} orders.")
    db.close()

if __name__ == "__main__":
    main()