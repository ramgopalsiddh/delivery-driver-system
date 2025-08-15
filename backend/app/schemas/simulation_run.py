from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SimulationRunBase(BaseModel):
    timestamp: datetime
    num_available_drivers: Optional[int] = None
    route_start_time: Optional[str] = None
    max_hours_per_driver_per_day: Optional[float] = None
    total_profit: float
    efficiency_score: float
    total_deliveries: int
    on_time_deliveries: int
    late_deliveries: int
    total_fuel_cost: float
    total_penalties: float
    total_bonuses: float

class SimulationRunCreate(SimulationRunBase):
    pass

class SimulationRun(SimulationRunBase):
    id: int

    class Config:
        from_attributes = True
