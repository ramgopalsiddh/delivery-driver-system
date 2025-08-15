from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class OrderBase(BaseModel):
    order_id: str
    value: float
    route_id: str
    delivery_time: datetime

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    value: Optional[float] = None
    route_id: Optional[str] = None
    delivery_time: Optional[datetime] = None
    assigned_driver_id: Optional[str] = None

class Order(OrderBase):
    id: int
    assigned_driver_id: Optional[str] = None

    class Config:
        from_attributes = True
