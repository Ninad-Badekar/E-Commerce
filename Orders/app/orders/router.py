from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.orders import crud, schemas

router = APIRouter(tags=["Orders"])

# Create a new order — triggers product finalization
@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order_in)

# Get a specific order by ID
@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)

# List all orders
@router.get("/", response_model=list[schemas.OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

# Update order status
@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status_in: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud.update_order_status(db, order_id, status_in.status)

# Cancel an order — triggers product release
@router.delete("/{order_id}", response_model=schemas.OrderCancelResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    crud.cancel_order(db, order_id)
    return {"detail": f"Order {order_id} canceled and reserved inventory released."}