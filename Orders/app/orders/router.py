from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.orders import crud, schemas

router = APIRouter(tags=["Orders"])

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, order_in)

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return crud.get_order(db, order_id)

@router.get("/", response_model=list[schemas.OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return crud.list_orders(db)

@router.patch("/{order_id}/status", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, status_in: schemas.OrderStatusUpdate, db: Session = Depends(get_db)):
    return crud.update_order_status(db, order_id, status_in.status)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    crud.cancel_order(db, order_id)
    return {"detail": "Order canceled and inventory updated."}
