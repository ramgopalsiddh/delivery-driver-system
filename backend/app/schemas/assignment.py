from datetime import datetime
from pydantic import BaseModel

class AssignmentBase(BaseModel):
    order_id: str
    driver_id: str
    estimated_delivery_time: datetime
    assigned_at: datetime

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int

    class Config:
        from_attributes = True
