from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    shift_hours_today = Column(Float)
    hours_worked_past_week = Column(Float)
