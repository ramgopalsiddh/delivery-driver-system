from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, unique=True, index=True)
    distance_km = Column(Float)
    traffic_level = Column(String)
    base_time_minutes = Column(Integer)

    orders = relationship("Order", back_populates="route")
