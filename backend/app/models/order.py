from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    value = Column(Float)
    route_id = Column(String, ForeignKey("routes.route_id"))
    delivery_time = Column(DateTime)
    assigned_driver_id = Column(String, ForeignKey("drivers.driver_id"), nullable=True)

    route = relationship("Route", back_populates="orders")
    assigned_driver = relationship("Driver")
