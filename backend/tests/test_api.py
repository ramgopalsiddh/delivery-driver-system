import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Depends # Import Depends
from fastapi import FastAPI # Import FastAPI

from app.main import app as main_app # Rename app to main_app to avoid conflict
from app.core.database import get_db

# Import necessary schemas and crud operations
from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.crud.user import create_user
from app.schemas.driver import DriverCreate
from app.schemas.order import OrderCreate
from app.schemas.route import RouteCreate
from app.schemas.user import UserCreate
from app.core.security import Hasher, get_current_user
from datetime import datetime, timedelta

# Import API routers
from app.api import auth, drivers, orders, optimization, routes, simulation_history

# Create a new FastAPI app instance for testing
test_app = FastAPI()

# Include routers with their prefixes and dependencies at the module level
test_app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
test_app.include_router(drivers.router, prefix="/drivers", dependencies=[Depends(get_current_user)])
test_app.include_router(orders.router, prefix="/orders", dependencies=[Depends(get_current_user)])
test_app.include_router(routes.router, prefix="/routes", dependencies=[Depends(get_current_user)])
test_app.include_router(optimization.router, prefix="/optimization", dependencies=[Depends(get_current_user)])
test_app.include_router(simulation_history.router, prefix="/simulation_history", dependencies=[Depends(get_current_user)])


# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def client(db_session_function):
    def override_get_db():
        try:
            yield db_session_function
        finally:
            db_session_function.close()
    test_app.dependency_overrides[get_db] = override_get_db

    # Mock get_current_user to return a dummy user for testing authenticated routes
    def override_get_current_user():
        return UserCreate(username="testuser", password="testpassword") # Only username is needed for auth checks

    test_app.dependency_overrides[get_current_user] = override_get_current_user

    yield TestClient(test_app)
    test_app.dependency_overrides.clear()

@pytest.fixture
def test_user_and_token(client, db_session_function):
    username = "testuser"
    password = "testpassword"
    
    # Register user
    client.post(
        "/auth/register",
        json={
            "username": username,
            "password": password
        }
    )

    # Login and get token
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password
        }
    )
    token = response.json()["access_token"]
    return username, token

@pytest.fixture(scope="module")
def setup_data_for_api(db_session_module):
    # Create drivers
    crud_driver.create_driver(db_session_module, DriverCreate(driver_id="D1", name="Driver A", shift_hours_today=4.0, hours_worked_past_week=20.0))
    crud_driver.create_driver(db_session_module, DriverCreate(driver_id="D2", name="Driver B", shift_hours_today=6.0, hours_worked_past_week=30.0))

    # Create routes
    crud_route.create_route(db_session_module, RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15))
    crud_route.create_route(db_session_module, RouteCreate(route_id="R2", distance_km=20.0, traffic_level="medium", base_time_minutes=30))

    # Create orders
    crud_order.create_order(db_session_module, OrderCreate(order_id="O1", value=50.0, route_id="R1", delivery_time=datetime.now() + timedelta(hours=1)))
    crud_order.create_order(db_session_module, OrderCreate(order_id="O2", value=75.0, route_id="R2", delivery_time=datetime.now() + timedelta(hours=2)))
    db_session_module.commit()

def test_read_drivers(client, setup_data_for_api, test_user_and_token):
    _, token = test_user_and_token
    response = client.get(
        "/drivers",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Driver A"

def test_read_orders(client, setup_data_for_api, test_user_and_token):
    _, token = test_user_and_token
    response = client.get(
        "/orders",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["value"] == 50.0

def test_read_routes(client, setup_data_for_api, test_user_and_token):
    _, token = test_user_and_token
    response = client.get(
        "/routes",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["traffic_level"] == "low"

def test_assign_orders_api(client, setup_data_for_api, test_user_and_token):
    _, token = test_user_and_token
    response = client.post(
        "/optimization/assign_orders",
        json={
            "num_available_drivers": 2,
            "route_start_time": "09:00",
            "max_hours_per_driver_per_day": 8.0
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert "Orders assigned successfully" in response.json()["message"]

def test_get_optimized_schedule_api(client, setup_data_for_api, test_user_and_token):
    _, token = test_user_and_token
    # First assign orders
    client.post(
        "/optimization/assign_orders",
        json={
            "num_available_drivers": 2,
            "route_start_time": "09:00",
            "max_hours_per_driver_per_day": 8.0
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    response = client.get(
        "/optimization/optimized_schedule",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert "schedule" in response.json()
    assert "kpis" in response.json()
    assert len(response.json()["schedule"]) > 0