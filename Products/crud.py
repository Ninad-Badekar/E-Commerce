from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
from typing import Tuple, Dict, Any, Optional, List
import models, schemas
from logger import log

def create_product_manual(db: Session, product: schemas.ProductCreate):
    try:
        db_product = models.Product(**product.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        log.info(f"Product created manually: ID={db_product.id}, Name={db_product.name}")
        return db_product
    except Exception as e:
        db.rollback()
        log.error(f"Failed to create product: {e}")
        raise

def get_all_products(db: Session):
    products = db.query(models.Product).all()
    log.info(f"Retrieved {len(products)} products")
    return products

def get_product_by_id(db: Session, id: int):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if product:
        log.info(f"Found product by ID={id}: {product.name}")
    else:
        log.warning(f"No product found with ID={id}")
    return product

def get_product_by_name(db: Session, name: str):
    return db.query(models.Product).filter(models.Product.name == name).first()

def get_product_by_brand(db: Session, brand: str):
    return db.query(models.Product).filter(models.Product.brand == brand).first()

def get_products_by_category(db: Session, category_id: int):
    products = db.query(models.Product).filter(models.Product.category_id == category_id).all()
    log.info(f"Found {len(products)} products for Category ID={category_id}")
    return products

def get_all_categories(db: Session):
    categories = db.query(models.Category).all()
    log.info(f"Retrieved {len(categories)} categories")
    return categories

def get_paginated_products(
    db: Session, 
    skip: int, 
    limit: int, 
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[int, List[models.Product]]:
    try:
        log.info(f"Fetching paginated products | Skip={skip}, Limit={limit}, Search={search}, Sort={sort_by} {sort_dir}, Filters={filters}")
        query = db.query(models.Product).options(joinedload(models.Product.category))
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    models.Product.name.like(search_term),
                    models.Product.brand.like(search_term)
                )
            )
        
        if filters:
            if filters.get('min_price'):
                query = query.filter(models.Product.price >= filters['min_price'])
            if filters.get('max_price'):
                query = query.filter(models.Product.price <= filters['max_price'])
            if filters.get('category_id'):
                query = query.filter(models.Product.category_id == filters['category_id'])
            if filters.get('in_stock_only'):
                query = query.filter(models.Product.stock_quantity > 0)

        total = query.count()

        if hasattr(models.Product, sort_by):
            sort_column = getattr(models.Product, sort_by)
            if sort_dir == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            log.warning(f"Invalid sort_by column '{sort_by}'")

        products = query.offset(skip).limit(limit).all()
        log.info(f"Returning {len(products)} products out of total {total}")
        return total, products
    
    except Exception as e:
        log.error(f"Error in get_paginated_products: {e}")
        raise

def update_product(db: Session, product_id: int, product_update: schemas.ProductUpdate):
    """Update a product with only the provided fields"""
    
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    if not db_product:
        db_product = db.query(models.Product).filter(models.Product.name == str(product_id)).first()
    
    if not db_product:
        db_product = db.query(models.Product).filter(models.Product.brand == str(product_id)).first()
    
    if not db_product:
        return None
    
    update_data = product_update.model_dump(exclude_unset=True)
    
    if 'attributes' in update_data:
        new_attributes = update_data.pop('attributes')
        
        if new_attributes is not None:
            existing_attributes = db_product.attributes or {}
            
            if isinstance(new_attributes, dict) and new_attributes:
                merged_attributes = dict(existing_attributes)
                merged_attributes.update(new_attributes)
                db_product.attributes = merged_attributes
            elif new_attributes == {}:
                db_product.attributes = {}
                
    for field, value in update_data.items():
        if hasattr(db_product, field):
            setattr(db_product, field, value)
    
    try:
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise e
    
def get_inventory_by_product_id(db: Session, product_id: int):
    return db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()

def update_inventory_quantity(db: Session, product_id: int, quantity_delta: int, reason: str = None, order_id: int = None):
    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory:
        raise Exception("Inventory record not found for product_id")

    inventory.quantity_available += quantity_delta
    inventory.quantity_available = max(0, inventory.quantity_available)

    movement = models.StockMovement(
        product_id=product_id,
        order_id=order_id,
        change=quantity_delta,
        reason=reason
        )
    db.add(movement)
    db.commit()
    db.refresh(inventory)
    return inventory

def create_or_update_inventory(db: Session, product_id: int, data: schemas.InventoryBase):
    inventory = get_inventory_by_product_id(db, product_id)
    if not inventory:
        inventory = models.Inventory(product_id=product_id, **data.model_dump())
        db.add(inventory)
    else:
        for key, value in data.model_dump().items():
            setattr(inventory, key, value)
    db.commit()
    db.refresh(inventory)
    return inventory

def get_stock_movements_for_product(db: Session, product_id: int):
    return db.query(models.StockMovement).filter(models.StockMovement.product_id == product_id).order_by(models.StockMovement.timestamp.desc()).all()


def update_inventory_settings(
    db: Session,
    product_id: int,
    update_data: schemas.InventoryUpdate
):
    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()
    if not inventory:
        raise Exception("Inventory not found")

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(inventory, key, value)

    db.commit()
    db.refresh(inventory)
    return inventory

def reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
    """Reserve stock with proper transaction management"""
    try:
        inventory = get_inventory_by_product_id(db, product_id)
        if not inventory or inventory.quantity_available < quantity:
            return False
            
        inventory.quantity_available -= quantity
        inventory.quantity_reserve += quantity
        
        movement = models.StockMovement(
            product_id=product_id,
            change=-quantity,
            reason="reserved"
        )
        db.add(movement)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e