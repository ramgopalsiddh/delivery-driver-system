import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.driver import Driver
from app.models.order import Order
from app.models.route import Route
from app.models.assignment import Assignment
from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.schemas.driver import DriverCreate
from app.schemas.order import OrderCreate
from app.schemas.route import RouteCreate
from datetime import datetime, timedelta

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

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def setup_data_for_api(db_session):
    # Create drivers
    crud_driver.create_driver(db_session, DriverCreate(driver_id="D1", name="Driver A", shift_hours_today=4.0, hours_worked_past_week=20.0))
    crud_driver.create_driver(db_session, DriverCreate(driver_id="D2", name="Driver B", shift_hours_today=6.0, hours_worked_past_week=30.0))

    # Create routes
    crud_route.create_route(db_session, RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15))
    crud_route.create_route(db_session, RouteCreate(route_id="R2", distance_km=20.0, traffic_level="medium", base_time_minutes=30))

    # Create orders
    crud_order.create_order(db_session, OrderCreate(order_id="O1", value=50.0, route_id="R1", delivery_time=datetime.now() + timedelta(hours=1)))
    crud_order.create_order(db_session, OrderCreate(order_id="O2", value=75.0, route_id="R2", delivery_time=datetime.now() + timedelta(hours=2)))
    db_session.commit()

def test_read_drivers(client, setup_data_for_api):
    response = client.get("/drivers")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Driver A"

def test_read_orders(client, setup_data_for_api):
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["value"] == 50.0

def test_read_routes(client, setup_data_for_api):
    response = client.get("/routes")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["traffic_level"] == "low"

def test_assign_orders_api(client, setup_data_for_api):
    response = client.post("/assign_orders")
    assert response.status_code == 200
    assert "Orders assigned successfully" in response.json()["message"]

def test_get_optimized_schedule_api(client, setup_data_for_api):
    # First assign orders
    client.post("/assign_orders")

    response = client.get("/optimized_schedule")
    assert response.status_code == 200
    assert len(response.json()) == 2 # Two orders were created and should be assigned
    assert "order_id" in response.json()[0]
    assert "driver_name" in response.json()[0]
