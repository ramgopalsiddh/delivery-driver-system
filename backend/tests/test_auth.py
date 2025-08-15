import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
from fastapi import Depends, HTTPException # Import Depends and HTTPException
from fastapi import FastAPI # Import FastAPI

from app.main import app as main_app # Rename app to main_app to avoid conflict
from app.core.database import get_db

from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import Hasher, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from datetime import timedelta

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

@pytest.fixture(scope="function")
def client_unauthenticated(db_session_function):
    def override_get_db():
        try:
            yield db_session_function
        finally:
            db_session_function.close()
    test_app.dependency_overrides[get_db] = override_get_db

    # Override get_current_user to simulate unauthenticated access
    def override_get_current_user_unauthenticated():
        raise HTTPException(status_code=401, detail="Not authenticated")

    test_app.dependency_overrides[get_current_user] = override_get_current_user_unauthenticated

    yield TestClient(test_app)
    test_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session_function):
    username = f"testuser_{uuid.uuid4()}"
    password = "testpassword"
    hashed_password = Hasher.get_password_hash(password)
    user = create_user(db_session_function, user=UserCreate(username=username, password=password), hashed_password=hashed_password)
    return user, password

def test_register_user(client, db_session_function):
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "password": "newpassword"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"
    assert "id" in response.json()

def test_login_for_access_token(client, db_session_function, test_user):
    username, password = test_user
    response = client.post(
        "/auth/token",
        data={
            "username": username.username,
            "password": password
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client, db_session_function):
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_protected_route_access(client, db_session_function, test_user):
    username, password = test_user
    login_response = client.post(
        "/auth/token",
        data={
            "username": username.username,
            "password": password
        }
    )
    token = login_response.json()["access_token"]

    # Assuming /drivers is a protected route
    protected_response = client.get(
        "/drivers",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert protected_response.status_code == 200 # Should be 200 if authenticated

def test_protected_route_no_token(client_unauthenticated, db_session_function):
    # Assuming /drivers is a protected route
    protected_response = client_unauthenticated.get("/drivers")
    assert protected_response.status_code == 401
    assert "Not authenticated" in protected_response.json()["detail"]

def test_protected_route_invalid_token(client_unauthenticated, db_session_function):
    # Assuming /drivers is a protected route
    protected_response = client_unauthenticated.get(
        "/drivers",
        headers={
            "Authorization": "Bearer invalidtoken"
        }
    )
    assert protected_response.status_code == 401
    assert "Could not validate credentials" in protected_response.json()["detail"]

# Note: Testing token expiration requires mocking datetime or waiting, which is more complex for a simple unit test.
# It's usually covered by integration tests or manual verification.