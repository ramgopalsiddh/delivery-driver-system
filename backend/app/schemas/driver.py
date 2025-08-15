from pydantic import BaseModel
from typing import Optional

class DriverBase(BaseModel):
    driver_id: str
    name: str
    shift_hours_today: float
    hours_worked_past_week: float

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    name: Optional[str] = None
    shift_hours_today: Optional[float] = None
    hours_worked_past_week: Optional[float] = None

class Driver(DriverBase):
    id: int

    class Config:
        from_attributes = True
