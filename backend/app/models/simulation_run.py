from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    num_available_drivers = Column(Integer)
    route_start_time = Column(String)
    max_hours_per_driver_per_day = Column(Float)
    total_profit = Column(Float)
    efficiency_score = Column(Float)
    total_deliveries = Column(Integer)
    on_time_deliveries = Column(Integer)
    late_deliveries = Column(Integer)
    total_fuel_cost = Column(Float)
    total_penalties = Column(Float)
    total_bonuses = Column(Float)
    # Store assignments as JSON string for simplicity, or link to individual assignments
    # For now, just storing KPIs and inputs as requested for history
