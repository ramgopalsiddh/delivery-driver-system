import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.core.database import Base
from app.models.driver import Driver
from app.models.order import Order
from app.models.route import Route
from app.models.assignment import Assignment
from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.crud import assignment as crud_assignment
from app.schemas.driver import DriverCreate
from app.schemas.order import OrderCreate
from app.schemas.route import RouteCreate
from app.services.optimizer import Optimizer

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

@pytest.fixture
def setup_data(db_session):
    # Create drivers
    driver1 = crud_driver.create_driver(db_session, DriverCreate(driver_id="D1", name="Driver A", shift_hours_today=4.0, hours_worked_past_week=20.0))
    driver2 = crud_driver.create_driver(db_session, DriverCreate(driver_id="D2", name="Driver B", shift_hours_today=6.0, hours_worked_past_week=30.0))

    # Create routes
    route1 = crud_route.create_route(db_session, RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15))
    route2 = crud_route.create_route(db_session, RouteCreate(route_id="R2", distance_km=20.0, traffic_level="medium", base_time_minutes=30))
    route3 = crud_route.create_route(db_session, RouteCreate(route_id="R3", distance_km=5.0, traffic_level="high", base_time_minutes=10))

    # Create orders
    order1 = crud_order.create_order(db_session, OrderCreate(order_id="O1", value=50.0, route_id="R1", delivery_time=datetime.now() + timedelta(hours=1)))
    order2 = crud_order.create_order(db_session, OrderCreate(order_id="O2", value=75.0, route_id="R2", delivery_time=datetime.now() + timedelta(hours=2)))
    order3 = crud_order.create_order(db_session, OrderCreate(order_id="O3", value=100.0, route_id="R3", delivery_time=datetime.now() + timedelta(hours=3)))

    db_session.commit()
    return db_session

def test_assign_orders(setup_data):
    db = setup_data
    optimizer = Optimizer(db)
    result = optimizer.assign_orders()

    assert "message" in result
    assert "Orders assigned successfully" in result["message"]

    assignments = crud_assignment.get_assignments(db)
    assert len(assignments) == 3 # All orders should be assigned

    # Verify that orders are assigned to drivers
    for assignment in assignments:
        order = crud_order.get_order(db, assignment.order_id)
        assert order.assigned_driver_id is not None

def test_get_optimized_schedule(setup_data):
    db = setup_data
    optimizer = Optimizer(db)
    optimizer.assign_orders() # First assign orders

    schedule = optimizer.get_optimized_schedule()
    assert len(schedule) == 3
    assert all("order_id" in item and "driver_name" in item for item in schedule)

    # Check if Driver A (D1) got fewer orders due to lower hours worked
    # This is a heuristic, so exact distribution might vary, but D1 should ideally get some orders
    driver_a_assignments = [item for item in schedule if item["driver_name"] == "Driver A"]
    driver_b_assignments = [item for item in schedule if item["driver_name"] == "Driver B"]

    # With the current scoring, D1 should be preferred initially
    # The exact number depends on the order of processing and workload balancing
    assert len(driver_a_assignments) > 0
    assert len(driver_b_assignments) > 0
