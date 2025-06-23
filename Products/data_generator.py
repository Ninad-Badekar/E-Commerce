import random
from typing import List, Dict, Any
from faker import Faker
from sqlalchemy.orm import Session
from models import Product, Category, PriceHistory
from logger import log

class DataGenerator:
    def __init__(self):
        self.faker = Faker()
        self.global_categories = [
            "Fashion", "Electronics", "Home & Garden", "Food & Beverage",
            "Health & Beauty", "Books & Media", "Toys & Games",
            "Sports & Outdoors", "DIY & Hardware", "Furniture"
        ]
        self.category_subcategories = {
            "Fashion": ["Clothing", "Footwear", "Accessories"],
            "Electronics": ["Mobiles", "Laptops", "Appliances"],
            "Home & Garden": ["Decor", "Plants", "Kitchen"],
            "Food & Beverage": ["Snacks", "Drinks", "Groceries"],
            "Health & Beauty": ["Skincare", "Supplements", "Makeup"],
            "Books & Media": ["Books", "Magazines", "E-books"],
            "Toys & Games": ["Board Games", "Action Figures", "Educational"],
            "Sports & Outdoors": ["Fitness", "Cycling", "Camping"],
            "DIY & Hardware": ["Tools", "Paint", "Electrical"],
            "Furniture": ["Bedroom", "Office", "Living Room"]
        }
        self.brand_names = [
            "Astra", "Zenex", "Nova", "UrbanMode", "GearPro",
            "CraftHaus", "NextEra", "Skyline", "PureEssence", "Flytek"
        ]

    def create_categories(self, db: Session) -> List[Category]:
        log.info("Creating initial categories and subcategories...")
        categories = []
        try:
            for main_name in self.global_categories:
                main_cat = Category(name=main_name)
                db.add(main_cat)
                db.flush()
                categories.append(main_cat)

                sub_names = self.category_subcategories.get(main_name, [])
                for sub in sub_names:
                    sub_cat = Category(name=f"{main_name} - {sub}", parent_id=main_cat.id)
                    db.add(sub_cat)
                    db.flush()
                    categories.append(sub_cat)
            db.commit()
            log.info(f"Created {len(categories)} categories (including subcategories).")
        except Exception as e:
            db.rollback()
            log.error(f"Error while creating categories: {e}")
        return categories

    def generate_brand(self) -> str:
        return random.choice([
            random.choice(self.brand_names),
            f"{self.faker.last_name()} {random.choice(['Inc', 'Corp', 'Ltd', 'Group'])}",
            f"{self.faker.country_code()} Tech",
            f"{self.faker.word().capitalize()}Works"
        ])

    def generate_product_attributes(self, category_name: str) -> Dict[str, Any]:
        return {
            "color": self.faker.color_name(),
            "weight": (
                f"{random.uniform(0.2, 3.0):.2f} kg"
                if "Electronics" in category_name or "Toys" in category_name
                else f"{random.uniform(5.0, 50.0):.2f} kg"
                if "Furniture" in category_name
                else f"{random.uniform(0.5, 10.0):.2f} kg"
            ),
            "material": (
                random.choice(["Cotton", "Polyester", "Denim", "Wool", "Silk"])
                if "Fashion" in category_name
                else random.choice(["Wood", "Metal", "Glass", "Plastic", "Leather"])
                if "Furniture" in category_name
                else random.choice(["Plastic", "Aluminum", "Glass"])
            ),
            "rating": round(random.uniform(3.0, 5.0), 1)
        }

    def create_products(self, db: Session, categories: List[Category], count: int) -> List[Product]:
        log.info(f"Generating {count} product(s)...")
        products = []
        
        # Map categories that require expiry dates
        categories_with_expiry = {
            "Food & Beverage", "Health & Beauty"
        }
        
        try:
            for _ in range(count):
                if not categories:
                    raise ValueError("No categories available. Please create categories first.")
                category = random.choice(categories)

                stock_quantity = random.randint(0, 1000)

                # Inlined generate_product logic
                product_data = {
                    "name": f"{self.faker.word().capitalize()} {self.faker.word().capitalize()}",
                    "price": round(
                        random.uniform(200.0, 2000.0)
                        if "Electronics" in category.name or "Furniture" in category.name
                        else random.uniform(50.0, 500.0)
                        if "Fashion" in category.name
                        else random.uniform(10.0, 300.0),
                        2
                    ),
                    "category_id": category.id,
                    "brand": self.generate_brand(),
                    "attributes": self.generate_product_attributes(category.name)
                }

                product = Product(**product_data)
                db.add(product)
                db.flush()  # Ensure product.id is available for Inventory

                # ✅ Create complete Inventory for this product
                from models import Inventory
                from datetime import datetime, timedelta
                
                # Determine expiry date based on category
                if category.name in categories_with_expiry:
                    expiry_date = datetime.now() + timedelta(days=random.randint(30, 365))
                else:
                    expiry_date = datetime(9999, 12, 31)  # Sentinel for "no expiry"
                
                inventory = Inventory(
                    product_id=product.id,
                    quantity_available=stock_quantity,
                    quantity_reserve=random.randint(0, min(50, stock_quantity // 4)),  # Reserve some stock
                    reorder_level=random.randint(5, 25),  # Random reorder level
                    reorder_quantity=random.randint(20, 100),  # Random reorder quantity
                    unit_cost=round(product_data["price"] * random.uniform(0.4, 0.7), 2),  # Cost is 40-70% of selling price
                    last_restocked=datetime.now() - timedelta(days=random.randint(1, 30)),  # Recently restocked
                    expiry_date=expiry_date,
                    batch_number=self.faker.uuid4(),
                    location=self.faker.city()
                    # last_updated will be set automatically by the model's default
                )
                db.add(inventory)

                products.append(product)

            db.commit()
            log.info(f"Successfully created {len(products)} products with complete inventory records.")
        except Exception as e:
            db.rollback()
            log.error(f"Failed to create products: {e}")
        return products


    def randomly_update_prices(self, db: Session, products: List[Product], batch_size: int = 50, reason: str = "auto_scheduler") -> None:
        log.info("Starting batch price update...")
        try:
            selected = random.sample(products, min(batch_size, len(products)))
            for product in selected:
                old_price = product.price
                change_percent = random.uniform(-0.2, 0.2)
                new_price = round(old_price * (1 + change_percent), 2)
                new_price = max(new_price, 1.0)

                price_history = PriceHistory(
                    product_id=product.id,
                    old_price=old_price,
                    new_price=new_price,
                    reason=reason
                )

                product.price = new_price
                db.add(price_history)

            db.commit()
            log.info(f"Updated prices for {len(selected)} product(s).")
        except Exception as e:
            db.rollback()
            log.error(f"Batch price update failed: {e}")

    def randomly_update_stocks(self, db: Session, products: List[Product], batch_size: int = 50) -> None:
        log.info("Starting batch stock update with inventory management...")
        try:
            from models import Inventory
            from datetime import datetime
            
            selected = random.sample(products, min(batch_size, len(products)))
            restocked_count = 0
            updated_count = 0
            
            for product in selected:
                # Get the inventory record for this product
                inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
                
                if not inventory:
                    log.warning(f"No inventory record found for product {product.id}")
                    continue
                
                # Simulate stock changes with realistic business scenarios
                scenario = random.choices(
                    ["normal_sales", "heavy_sales", "slow_sales", "restock"],
                    weights=[60, 25, 10, 5]  # 60% normal, 25% heavy sales, 10% slow, 5% restock
                )[0]
                
                if scenario == "heavy_sales":
                    change = random.randint(-100, -30)  # Big sales day
                elif scenario == "normal_sales":
                    change = random.randint(-30, -5)   # Regular sales
                elif scenario == "slow_sales":
                    change = random.randint(-10, 0)    # Slow day
                else:  # restock
                    change = random.randint(20, 100)   # Manual restock
                old_quantity = inventory.quantity_available
                new_quantity = max(0, inventory.quantity_available + change)
                
                # Update inventory and product
                inventory.quantity_available = new_quantity
                product.stock_quantity = new_quantity
                
                # Auto-restock if below reorder level (but not always - 20% chance)
                if new_quantity <= inventory.reorder_level and old_quantity > inventory.reorder_level:
                    if random.random() < 0.2:  # Only 20% chance of auto-restock (was 30%)
                        inventory.quantity_available += inventory.reorder_quantity
                        product.stock_quantity += inventory.reorder_quantity
                        inventory.last_restocked = datetime.now()
                        inventory.batch_number = self.faker.uuid4()
                        restocked_count += 1
                
                updated_count += 1

            db.commit()
            log.info(f"Updated stock for {updated_count} product(s). Auto-restocked {restocked_count} product(s).")
            
        except Exception as e:
            db.rollback()
            log.error(f"Batch stock update failed: {e}")

    def get_categories(self, db: Session) -> List[Category]:
        categories = db.query(Category).all()
        log.info(f"Retrieved {len(categories)} categories from database.")
        return categories

