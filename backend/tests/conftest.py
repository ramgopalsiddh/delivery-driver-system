import os
from dotenv import load_dotenv
from app.core.database import Base, engine, SessionLocal # New import
import pytest

# Load environment variables from .env.example for testing
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.example'), override=True)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Import all models to ensure Base.metadata is aware of them for table creation
    import app.models.driver
    import app.models.order
    import app.models.route
    import app.models.assignment
    import app.models.user
    import app.models.simulation_run
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session_function():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def db_session_module():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def db_session_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()