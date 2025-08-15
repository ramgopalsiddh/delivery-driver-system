from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SimulationInput(BaseModel):
    num_available_drivers: Optional[int] = Field(None, ge=1, description="Number of drivers available for the simulation.")
    route_start_time: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", description="Start time for routes in HH:MM format.")
    max_hours_per_driver_per_day: Optional[float] = Field(None, ge=0, description="Maximum hours a driver can work per day.")

class KpiData(BaseModel):
    total_profit: float
    efficiency_score: float
    total_deliveries: int
    on_time_deliveries: int
    late_deliveries: int
    total_fuel_cost: float
    total_penalties: float
    total_bonuses: float

class OptimizedScheduleResponse(BaseModel):
    schedule: List[Dict[str, Any]]
    kpis: Optional[KpiData] = None