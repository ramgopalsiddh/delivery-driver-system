from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate

def get_order(db: Session, order_id: str):
    return db.query(Order).filter(Order.order_id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def create_or_update_order(db: Session, order: OrderCreate):
    db_order = db.query(Order).filter(Order.order_id == order.order_id).first()
    if db_order:
        for key, value in order.model_dump().items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
        return db_order
    else:
        return create_order(db, order)

def assign_order_to_driver(db: Session, order_id: str, driver_id: str):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order:
        db_order.assigned_driver_id = driver_id
        db.commit()
        db.refresh(db_order)
    return db_order

def update_order(db: Session, order_id: str, order_data: dict):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order:
        for key, value in order_data.items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
        return db_order
    return None

def delete_order(db: Session, order_id: str):
    db_order = db.query(Order).filter(Order.order_id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False
