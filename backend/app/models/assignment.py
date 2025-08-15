from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.core.database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.order_id"), unique=True, index=True)
    driver_id = Column(String, ForeignKey("drivers.driver_id"), index=True)
    estimated_delivery_time = Column(DateTime)
    assigned_at = Column(DateTime)
