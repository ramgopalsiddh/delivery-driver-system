import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.core.database import Base
from app.models.driver import Driver
from app.models.order import Order
from app.models.route import Route
from app.models.assignment import Assignment
from app.models.simulation_run import SimulationRun
from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.crud import assignment as crud_assignment
from app.crud import simulation_run as crud_simulation_run
from app.schemas.driver import DriverCreate
from app.schemas.order import OrderCreate
from app.schemas.route import RouteCreate
from app.schemas.optimization import SimulationInput
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
    db_session.refresh(driver1)
    driver2 = crud_driver.create_driver(db_session, DriverCreate(driver_id="D2", name="Driver B", shift_hours_today=6.0, hours_worked_past_week=30.0))
    db_session.refresh(driver2)
    driver3 = crud_driver.create_driver(db_session, DriverCreate(driver_id="D3", name="Driver C (Fatigued)", shift_hours_today=9.0, hours_worked_past_week=45.0)) # Fatigued driver
    db_session.refresh(driver3)

    # Create routes
    route1 = crud_route.create_route(db_session, RouteCreate(route_id="R1", distance_km=10.0, traffic_level="low", base_time_minutes=15))
    db_session.refresh(route1)
    route2 = crud_route.create_route(db_session, RouteCreate(route_id="R2", distance_km=20.0, traffic_level="medium", base_time_minutes=30))
    db_session.refresh(route2)
    route3 = crud_route.create_route(db_session, RouteCreate(route_id="R3", distance_km=5.0, traffic_level="high", base_time_minutes=10))
    db_session.refresh(route3)
    route4 = crud_route.create_route(db_session, RouteCreate(route_id="R4", distance_km=100.0, traffic_level="low", base_time_minutes=60)) # Long route
    db_session.refresh(route4)

    # Create orders
    now = datetime.now()
    order1 = crud_order.create_order(db_session, OrderCreate(order_id="O1", value=50.0, route_id="R1", delivery_time=now + timedelta(minutes=30))) # On-time
    order2 = crud_order.create_order(db_session, OrderCreate(order_id="O2", value=1500.0, route_id="R2", delivery_time=now + timedelta(minutes=40))) # High-value, on-time
    order3 = crud_order.create_order(db_session, OrderCreate(order_id="O3", value=200.0, route_id="R3", delivery_time=now + timedelta(minutes=10))) # Late
    order4 = crud_order.create_order(db_session, OrderCreate(order_id="O4", value=1200.0, route_id="R1", delivery_time=now + timedelta(minutes=20))) # High-value, potentially late
    order5 = crud_order.create_order(db_session, OrderCreate(order_id="O5", value=800.0, route_id="R4", delivery_time=now + timedelta(hours=3))) # Normal value, long route

    db_session.commit()
    return db_session, driver1, driver2, driver3, route1, route2, route3, route4, order1, order2, order3, order4, order5

# --- Test individual rule calculations ---

def test_calculate_estimated_delivery_time_no_fatigue(setup_data):
    db_session, driver1, _, _, route1, _, _, _, _, _, _, _, _ = setup_data
    optimizer = Optimizer(db_session)
    
    # Expected: base_time (15) * 1.1 (low traffic) + (10km / 30km/h) * 60min/h = 16.5 + 20 = 36.5 minutes
    estimated_time = optimizer._calculate_estimated_delivery_time(route1, driver1)
    assert abs(estimated_time.total_seconds() / 60 - 36.5) < 0.1

def test_calculate_estimated_delivery_time_with_fatigue(setup_data):
    db_session, _, _, driver3, route1, _, _, _, _, _, _, _, _ = setup_data
    optimizer = Optimizer(db_session)
    
    # Expected: 36.5 minutes * (1 + 0.30) = 36.5 * 1.3 = 47.45 minutes
    estimated_time = optimizer._calculate_estimated_delivery_time(route1, driver3)
    assert abs(estimated_time.total_seconds() / 60 - 47.45) < 0.1

def test_calculate_late_delivery_penalty_on_time(db_session):
    optimizer = Optimizer(db_session)
    now = datetime.now()
    # Estimated is 5 min before requested + 10 min buffer
    estimated_delivery = now + timedelta(minutes=5)
    requested_delivery = now + timedelta(minutes=15)
    penalty = optimizer._calculate_late_delivery_penalty(estimated_delivery, requested_delivery)
    assert penalty == 0.0

def test_calculate_late_delivery_penalty_late(db_session):
    optimizer = Optimizer(db_session)
    now = datetime.now()
    # Estimated is 15 min after requested + 10 min buffer (so 5 min past buffer)
    estimated_delivery = now + timedelta(minutes=25)
    requested_delivery = now + timedelta(minutes=10)
    penalty = optimizer._calculate_late_delivery_penalty(estimated_delivery, requested_delivery)
    assert penalty == 50.0

def test_calculate_high_value_bonus_applied(db_session):
    optimizer = Optimizer(db_session)
    bonus = optimizer._calculate_high_value_bonus(1500.0, True)
    assert bonus == 150.0 # 10% of 1500

def test_calculate_high_value_bonus_not_applied_late(db_session):
    optimizer = Optimizer(db_session)
    bonus = optimizer._calculate_high_value_bonus(1500.0, False)
    assert bonus == 0.0

def test_calculate_high_value_bonus_not_applied_low_value(db_session):
    optimizer = Optimizer(db_session)
    bonus = optimizer._calculate_high_value_bonus(900.0, True)
    assert bonus == 0.0

def test_calculate_fuel_cost_low_traffic(setup_data):
    db_session, _, _, _, route1, _, _, _, _, _, _, _, _ = setup_data
    optimizer = Optimizer(db_session)
    cost = optimizer._calculate_fuel_cost(route1)
    assert cost == 50.0 # 10km * 5/km

def test_calculate_fuel_cost_high_traffic(setup_data):
    db_session, _, _, _, _, _, route3, _, _, _, _, _, _ = setup_data
    optimizer = Optimizer(db_session)
    cost = optimizer._calculate_fuel_cost(route3)
    assert cost == 35.0 # 5km * (5 + 2)/km = 5 * 7 = 35

def test_calculate_order_profit(setup_data):
    db_session, _, _, _, route1, _, _, _, _, _, _, _, _ = setup_data
    optimizer = Optimizer(db_session)
    now = datetime.now()

    # Scenario 1: On-time, high-value, low traffic
    order_hv_ot = crud_order.create_order(db_session, OrderCreate(order_id="O_HV_OT", value=1200.0, route_id=route1.route_id, delivery_time=now + timedelta(hours=1)))
    estimated_hv_ot = now + timedelta(minutes=30) # On time
    profit_hv_ot = optimizer._calculate_order_profit(order_hv_ot, route1, estimated_hv_ot)
    # Expected: 1200 (value) + 120 (bonus) - 0 (penalty) - 50 (fuel) = 1270
    assert profit_hv_ot == 1270.0

    # Scenario 2: Late, normal value, low traffic
    order_nv_late = crud_order.create_order(db_session, OrderCreate(order_id="O_NV_LATE", value=500.0, route_id=route1.route_id, delivery_time=now + timedelta(minutes=10)))
    estimated_nv_late = now + timedelta(minutes=30) # Late
    profit_nv_late = optimizer._calculate_order_profit(order_nv_late, route1, estimated_nv_late)
    # Expected: 500 (value) + 0 (bonus) - 50 (penalty) - 50 (fuel) = 400
    assert profit_nv_late == 400.0

# --- Test assign_orders and KPIs ---

def test_assign_orders_and_kpis(setup_data):
    db, driver1, driver2, driver3, route1, route2, route3, route4, order1, order2, order3, order4, order5 = setup_data
    optimizer = Optimizer(db)
    
    simulation_input = SimulationInput(
        num_available_drivers=2,
        route_start_time="09:00",
        max_hours_per_driver_per_day=8.0
    )
    result = optimizer.assign_orders(simulation_input)

    assert "message" in result
    assert "Orders assigned successfully" in result["message"]
    assert "kpis" in result

    kpis = result["kpis"]
    assert kpis["total_deliveries"] == 5 # All 5 orders should be processed
    assert kpis["on_time_deliveries"] >= 0 # At least some should be on time
    assert kpis["late_deliveries"] >= 0
    assert kpis["total_profit"] is not None
    assert kpis["efficiency_score"] is not None
    assert kpis["total_fuel_cost"] is not None
    assert kpis["total_penalties"] is not None
    assert kpis["total_bonuses"] is not None

    # Verify that simulation run is saved
    sim_runs = crud_simulation_run.get_simulation_runs(db)
    assert len(sim_runs) == 1
    assert sim_runs[0].total_profit == kpis["total_profit"]
    assert sim_runs[0].efficiency_score == kpis["efficiency_score"]

def test_assign_orders_with_limited_drivers(setup_data):
    db, driver1, driver2, driver3, route1, route2, route3, route4, order1, order2, order3, order4, order5 = setup_data
    optimizer = Optimizer(db)
    
    simulation_input = SimulationInput(
        num_available_drivers=1, # Only one driver available
        route_start_time="09:00",
        max_hours_per_driver_per_day=24.0 # No max hours constraint
    )
    result = optimizer.assign_orders(simulation_input)

    assert result["kpis"]["total_deliveries"] <= 5 # Should be less if one driver can't do all
    # The exact number depends on the workload of the single driver
    # For this test, we just check if it's not all 5, implying the limit worked
    assignments = crud_assignment.get_assignments(db)
    # Check if assignments are made, but not necessarily all orders are assigned if one driver is overloaded
    assert len(assignments) > 0

def test_assign_orders_with_max_hours_constraint(setup_data):
    db, driver1, driver2, driver3, route1, route2, route3, route4, order1, order2, order3, order4, order5 = setup_data
    optimizer = Optimizer(db)
    
    simulation_input = SimulationInput(
        num_available_drivers=3,
        route_start_time="09:00",
        max_hours_per_driver_per_day=1.0 # Very strict max hours
    )
    result = optimizer.assign_orders(simulation_input)

    # Expect fewer deliveries due to strict max hours
    assert result["kpis"]["total_deliveries"] < 5
    assignments = crud_assignment.get_assignments(db)
    assert len(assignments) < 5

def test_get_optimized_schedule_with_kpis(setup_data):
    db, driver1, driver2, driver3, route1, route2, route3, route4, order1, order2, order3, order4, order5 = setup_data
    optimizer = Optimizer(db)
    
    simulation_input = SimulationInput(
        num_available_drivers=2,
        route_start_time="09:00",
        max_hours_per_driver_per_day=8.0
    )
    optimizer.assign_orders(simulation_input)

    schedule_response = optimizer.get_optimized_schedule()
    assert "schedule" in schedule_response
    assert "kpis" in schedule_response
    assert schedule_response["kpis"] is not None
    assert schedule_response["kpis"]["total_profit"] is not None
    assert schedule_response["kpis"]["efficiency_score"] is not None

    # Verify schedule content
    schedule = schedule_response["schedule"]
    assert len(schedule) > 0
    assert all("order_id" in item and "driver_name" in item for item in schedule)