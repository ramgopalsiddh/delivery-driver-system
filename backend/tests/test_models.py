import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.driver import Driver
from app.models.order import Order
from app.models.route import Route
from app.models.assignment import Assignment
from datetime import datetime, timedelta # New import

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_driver(db_session):
    driver = Driver(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    db_session.add(driver)
    db_session.commit()
    db_session.refresh(driver)
    assert driver.id is not None
    assert driver.name == "Test Driver"

def test_create_route(db_session):
    route = Route(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    db_session.add(route)
    db_session.commit()
    db_session.refresh(route)
    assert route.id is not None
    assert route.route_id == "R1"

def test_create_order(db_session):
    route = Route(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    db_session.add(route)
    db_session.commit()
    db_session.refresh(route)

    order = Order(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())

def test_create_assignment(db_session):
    driver = Driver(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    db_session.add(driver)
    
    route = Route(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    db_session.add(route)

    order = Order(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())
    db_session.add(order)
    db_session.commit()
    db_session.refresh(driver)
    db_session.refresh(route)
    db_session.refresh(order)

    assignment = Assignment(order_id="O1", driver_id="D1", estimated_delivery_time=datetime.now() + timedelta(minutes=30), assigned_at=datetime.now())
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    assert assignment.id is not None
    assert assignment.order_id == "O1"
    assert assignment.driver_id == "D1"
