import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
from app.schemas.assignment import AssignmentCreate

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

def test_create_and_get_driver(db_session):
    driver_in = DriverCreate(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    driver = crud_driver.create_driver(db_session, driver_in)
    assert driver.driver_id == "D1"
    assert crud_driver.get_driver(db_session, "D1").name == "Test Driver"

def test_create_and_get_route(db_session):
    route_in = RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    route = crud_route.create_route(db_session, route_in)
    assert route.route_id == "R1"
    assert crud_route.get_route(db_session, "R1").distance_km == 10.0

def test_create_and_get_order(db_session):
    route_in = RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    crud_route.create_route(db_session, route_in)

    order_in = OrderCreate(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())
    order = crud_order.create_order(db_session, order_in)
    assert order.order_id == "O1"
    assert crud_order.get_order(db_session, "O1").value == 100.0

def test_assign_order_to_driver(db_session):
    driver_in = DriverCreate(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    crud_driver.create_driver(db_session, driver_in)

    route_in = RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    crud_route.create_route(db_session, route_in)

    order_in = OrderCreate(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())
    crud_order.create_order(db_session, order_in)

    assigned_order = crud_order.assign_order_to_driver(db_session, "O1", "D1")
    assert assigned_order.assigned_driver_id == "D1"
    assert crud_order.get_order(db_session, "O1").assigned_driver_id == "D1"

def test_create_and_get_assignment(db_session):
    driver_in = DriverCreate(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    crud_driver.create_driver(db_session, driver_in)

    route_in = RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    crud_route.create_route(db_session, route_in)

    order_in = OrderCreate(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())
    crud_order.create_order(db_session, order_in)

    assignment_in = AssignmentCreate(
        order_id="O1", 
        driver_id="D1", 
        estimated_delivery_time=datetime.now(), 
        assigned_at=datetime.now()
    )
    assignment = crud_assignment.create_assignment(db_session, assignment_in)
    assert assignment.order_id == "O1"
    assert crud_assignment.get_assignment(db_session, "O1").driver_id == "D1"

def test_delete_all_assignments(db_session):
    driver_in = DriverCreate(driver_id="D1", name="Test Driver", shift_hours_today=8.0, hours_worked_past_week=40.0)
    crud_driver.create_driver(db_session, driver_in)

    route_in = RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15)
    crud_route.create_route(db_session, route_in)

    order_in = OrderCreate(order_id="O1", value=100.0, route_id="R1", delivery_time=datetime.now())
    crud_order.create_order(db_session, order_in)

    assignment_in = AssignmentCreate(
        order_id="O1", 
        driver_id="D1", 
        estimated_delivery_time=datetime.now(), 
        assigned_at=datetime.now()
    )
    crud_assignment.create_assignment(db_session, assignment_in)
    assert len(crud_assignment.get_assignments(db_session)) == 1

    crud_assignment.delete_all_assignments(db_session)
    assert len(crud_assignment.get_assignments(db_session)) == 0
