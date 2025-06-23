from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from typing import List, Optional, Union
import schemas, crud
from database import get_db
from data_generator import DataGenerator
from logger import log
import models

router = APIRouter(prefix="/products", tags=["Products"])
generator = DataGenerator()

@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    log.info(f"Creating product: {product.name}")
    return crud.create_product_manual(db, product)

@router.get("/", response_model=schemas.ProductListResponse)
def get_all_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search products"),
    sort_by: str = Query("created_at", description="Sort by field"),
    sort_dir: str = Query("desc", regex="^(asc|desc)$", description="Sort direction"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    in_stock_only: bool = Query(False, description="Show only in-stock items")
):
    log.info(f"Fetching products | page={page}, per_page={per_page}, search='{search}', sort_by='{sort_by}', sort_dir='{sort_dir}'")
    
    skip = (page - 1) * per_page
    filters = {
        'min_price': min_price,
        'max_price': max_price,
        'category_id': category_id,
        'in_stock_only': in_stock_only
    }
    
    total, products = crud.get_paginated_products(
        db, skip, per_page, search, sort_by, sort_dir, filters
    )
    
    clean_products = []
    for product in products:
        rating = None
        if product.attributes and 'rating' in product.attributes:
            rating = product.attributes['rating']
        
        clean_products.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "brand": product.brand,
            "stock_quantity": product.inventory.quantity_available if product.inventory else 0,
            "category_name": product.category.name if product.category else "Unknown",
            "rating": rating
        })
    
    total_pages = (total + per_page - 1) // per_page
    log.info(f"Found {len(products)} products (Total: {total}, Total Pages: {total_pages})")
    
    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "products": clean_products
    }

@router.get("/{product_id}", response_model=schemas.Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    log.info(f"Fetching product by ID: {product_id}")
    product = crud.get_product_by_id(db, product_id)
    if not product:
        log.warning(f"Product not found: ID {product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/auto-generate", response_model=List[schemas.Product])
def auto_generate_products(count: int = 1, db: Session = Depends(get_db)):
    log.info(f"Auto-generating {count} products")
    categories = crud.get_all_categories(db)
    return generator.create_products(db, categories, count)

from fastapi import Query

@router.post("/update-prices")
def update_all_prices(
    count: int = Query(50, ge=1, le=500, description="Number of products to update"),
    db: Session = Depends(get_db)
):
    log.info(f"Updating prices for {count} product(s)")
    products = crud.get_all_products(db)
    if not products:
        log.warning("No products found to update prices")
        return {"message": "No products found to update"}
    generator.randomly_update_prices(db, products, batch_size=count)
    return {"message": f"Price updated for {min(count, len(products))} products"}


@router.patch("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: str, 
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):

    product = None
    if product_id.isdigit():
        product = crud.get_product_by_id(db, int(product_id))
    if not product:
        product = crud.get_product_by_name(db, product_id)
    if not product:
        product = crud.get_product_by_brand(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_update.category_id is not None:
        valid_category_ids = [cat.id for cat in crud.get_all_categories(db)]
        if product_update.category_id not in valid_category_ids:
            raise HTTPException(status_code=400, detail="Invalid category_id")

    updated_product = crud.update_product(db, product.id, product_update)

    return updated_product

@router.get("/{product_id}/inventory", response_model=schemas.Inventory)
def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = crud.get_inventory_by_product_id(db, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

@router.patch("/{product_id}/inventory")
def adjust_inventory(
    product_id: int,
    quantity_delta: int,
    reason: str = "manual adjustment",
    order_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        updated_inventory = crud.update_inventory_quantity(
            db, product_id, quantity_delta, reason, order_id
        )
        return {
            "message": f"Inventory updated for Product ID {product_id}",
            "new_quantity": updated_inventory.quantity_available
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{product_id}/stock-movements", response_model=List[schemas.StockMovement])
def get_stock_movements(product_id: int, db: Session = Depends(get_db)):
    return crud.get_stock_movements_for_product(db, product_id)

@router.patch("/{product_id}/inventory/settings", response_model=schemas.Inventory)
def update_inventory_settings(
    product_id: int,
    inventory_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db)
):
    try:
        updated_inventory = crud.update_inventory_settings(
            db=db,
            product_id=product_id,
            update_data=inventory_update
        )
        return updated_inventory
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reserve", response_model=dict)
def reserve_products(
    reservations: Union[List[dict], dict],
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Reserve single or multiple products for an order (atomic operation)"""
    if isinstance(reservations, dict):
        reservations = [reservations]
    
    try:
        reserved_items = []
        
        for item in reservations:
            inventory = crud.get_inventory_by_product_id(db, item["product_id"])
            if not inventory or inventory.quantity_available < item["quantity"]:
                db.rollback()
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for product {item['product_id']} (requested: {item['quantity']}, available: {inventory.quantity_available if inventory else 0})"
                )
        
        for item in reservations:
            inventory = crud.get_inventory_by_product_id(db, item["product_id"])
            inventory.quantity_available -= item["quantity"]
            inventory.quantity_reserve += item["quantity"]
            
            movement = models.StockMovement(
                product_id=item["product_id"],
                order_id=item["order_id"],
                change=-item["quantity"],
                reason=f"reserve_order_{order_id}" if order_id else "reserve"
            )
            db.add(movement)
            reserved_items.append({
                **item,
                "remaining_available": inventory.quantity_available
            })
        
        db.commit()
        
        return {
            "success": True,
            "reserved_items": reserved_items,
            "total_items": len(reserved_items),
            "order_id": order_id,
            "message": f"Successfully reserved {len(reserved_items)} product(s)"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/release", response_model=dict)
def release_products(
    reservations: Union[List[dict], dict],
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Release single or multiple reserved products (e.g., if user cancels checkout)"""
    if isinstance(reservations, dict):
        reservations = [reservations]
    
    try:
        released_items = []
        
        for item in reservations:
            inventory = crud.get_inventory_by_product_id(db, item["product_id"])
            if inventory and inventory.quantity_reserve >= item["quantity"]:
                inventory.quantity_reserve -= item["quantity"]
                inventory.quantity_available += item["quantity"]
                
                movement = models.StockMovement(
                    product_id=item["product_id"],
                    order_id=item["order_id"],
                    change=item["quantity"],
                    reason=f"release_order_{order_id}" if order_id else "release"
                )
                db.add(movement)
                released_items.append({
                    **item,
                    "new_available": inventory.quantity_available
                })
        
        db.commit()
        return {
            "success": True,
            "released_items": released_items,
            "total_items": len(released_items),
            "order_id": order_id,
            "message": f"Successfully released {len(released_items)} product(s)"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/finalize", response_model=dict)
def finalize_products(
    reservations: Union[List[dict], dict],
    order_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Finalize single or multiple reserved products (convert reserves to sold)"""
    if isinstance(reservations, dict):
        reservations = [reservations]
    
    try:
        finalized_items = []
        
        for item in reservations:
            inventory = crud.get_inventory_by_product_id(db, item["product_id"])
            if inventory and inventory.quantity_reserve >= item["quantity"]:
                inventory.quantity_reserve -= item["quantity"]
                
                movement = models.StockMovement(
                    product_id=item["product_id"],
                    order_id=item["order_id"],
                    change=-item["quantity"],
                    reason=f"finalize_order_{order_id}" if order_id else "finalize"
                )
                db.add(movement)
                finalized_items.append({
                    **item,
                    "remaining_reserved": inventory.quantity_reserve
                })
        
        db.commit()
        return {
            "success": True,
            "finalized_items": finalized_items,
            "total_items": len(finalized_items),
            "order_id": order_id,
            "message": f"Successfully finalized {len(finalized_items)} product(s)"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/featured", response_model=List[dict])
def get_featured_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured/popular products for homepage"""
    products = db.query(models.Product)\
        .join(models.Inventory)\
        .filter(models.Inventory.quantity_available > 0)\
        .order_by(desc(models.Product.created_at))\
        .limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "brand": p.brand,
            "category_name": p.category.name if p.category else "Unknown",
            "rating": p.attributes.get("rating") if p.attributes else None,
            "stock_quantity": p.inventory.quantity_available if p.inventory else 0
        } for p in products
    ]

@router.get("/recommendations/{user_id}", response_model=List[dict])
def get_product_recommendations(
    user_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Get personalized product recommendations"""
    products = db.query(models.Product)\
        .join(models.Inventory)\
        .filter(models.Inventory.quantity_available > 0)\
        .order_by(func.random())\
        .limit(limit).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "brand": p.brand,
            "category_name": p.category.name if p.category else "Unknown",
            "rating": p.attributes.get("rating") if p.attributes else None,
            "stock_quantity": p.inventory.quantity_available if p.inventory else 0
        } for p in products
    ]