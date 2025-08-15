from pydantic import BaseModel
from typing import Optional

class RouteBase(BaseModel):
    route_id: str
    distance_km: float
    traffic_level: str
    base_time_minutes: int

class RouteCreate(RouteBase):
    pass

class RouteUpdate(BaseModel):
    distance_km: Optional[float] = None
    traffic_level: Optional[str] = None
    base_time_minutes: Optional[int] = None

class Route(RouteBase):
    id: int

    class Config:
        from_attributes = True
