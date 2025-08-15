import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.core.database import Base
from app.services.data_loader import load_all_data
from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route

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

def test_load_all_data(db_session):
    # Ensure the data directory exists for the test
    data_dir = "/home/ram/wd/delivery-driver-system/backend/data"
    os.makedirs(data_dir, exist_ok=True)

    # Create dummy CSV files for testing
    with open(os.path.join(data_dir, "drivers.csv"), "w") as f:
        f.write("driver_id|name|shift_hours_today|hours_worked_past_week\n")
        f.write("D1|Alice|8|40\n")
        f.write("D2|Bob|7|35\n")
    
    with open(os.path.join(data_dir, "orders.csv"), "w") as f:
        f.write("order_id,value,route_id,delivery_time\n")
        f.write("O1,100.0,R1,2025-08-12 10:00:00\n")
        f.write("O2,50.0,R2,2025-08-12 11:00:00\n")

    with open(os.path.join(data_dir, "routes.csv"), "w") as f:
        f.write("route_id,distance_km,traffic_level,base_time_minutes\n")
        f.write("R1,10.0,low,15\n")
        f.write("R2,20.0,medium,30\n")

    load_all_data(db_session)

    drivers = crud_driver.get_drivers(db_session)
    orders = crud_order.get_orders(db_session)
    routes = crud_route.get_routes(db_session)

    assert len(drivers) == 2
    assert drivers[0].name == "Alice"
    assert len(orders) == 2
    assert orders[0].value == 100.0
    assert len(routes) == 2
    assert routes[0].traffic_level == "low"

    # Clean up dummy CSV files
    os.remove(os.path.join(data_dir, "drivers.csv"))
    os.remove(os.path.join(data_dir, "orders.csv"))
    os.remove(os.path.join(data_dir, "routes.csv"))
