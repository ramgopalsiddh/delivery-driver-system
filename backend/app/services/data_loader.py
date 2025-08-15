import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime

from app.crud import driver as crud_driver
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.schemas.driver import DriverCreate
from app.schemas.order import OrderCreate
from app.schemas.route import RouteCreate

def load_drivers_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path, sep=',') # Read as comma-separated
    df.columns = df.columns.str.strip() # Strip whitespace from column names
    print(f"DEBUG: Columns detected in drivers.csv: {df.columns.tolist()}") # DEBUG PRINT
    for index, row in df.iterrows(): # Use index for generating driver_id
        # Parse past_week_hours from pipe-separated string to sum
        past_week_hours_list = [float(h) for h in str(row['past_week_hours']).split('|')]
        total_hours_past_week = sum(past_week_hours_list)

        driver_data = DriverCreate(
            driver_id=str(index + 1), # Generate unique driver_id as 1, 2, 3...
            name=row['name'],
            shift_hours_today=row['shift_hours'],
            hours_worked_past_week=total_hours_past_week
        )
        crud_driver.create_or_update_driver(db, driver_data)

def load_orders_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip() # Strip whitespace from column names
    for _, row in df.iterrows():
        # Combine today's date with the time from CSV
        delivery_time_str = str(row['delivery_time'])
        # Handle cases where delivery_time might be just time (HH:MM) or full datetime
        if len(delivery_time_str) <= 5: # Assuming HH:MM format
            today = datetime.now().date()
            delivery_datetime = datetime.strptime(f"{today} {delivery_time_str}", '%Y-%m-%d %H:%M')
        else:
            delivery_datetime = datetime.strptime(delivery_time_str, '%Y-%m-%d %H:%M:%S')

        order_data = OrderCreate(
            order_id=str(row['order_id']),
            value=row['value_rs'], # Use value_rs from CSV
            route_id=str(row['route_id']),
            delivery_time=delivery_datetime
        )
        created_order = crud_order.create_or_update_order(db, order_data)
        print(f"DEBUG: Loaded order {created_order.order_id}, assigned_driver_id: {created_order.assigned_driver_id}") # DEBUG

def load_routes_from_csv(db: Session, file_path: str):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip() # Strip whitespace from column names
    for _, row in df.iterrows():
        route_data = RouteCreate(
            route_id=str(row['route_id']),
            distance_km=row['distance_km'],
            traffic_level=row['traffic_level'],
            base_time_minutes=row['base_time_min'] # Use base_time_min from CSV
        )
        crud_route.create_or_update_route(db, route_data)

def load_all_data(db: Session):
    # Assuming CSVs are in the same directory as this script or accessible via relative path
    # For Docker, these paths will be relative to the container's working directory
    load_drivers_from_csv(db, "./data/drivers.csv")
    load_orders_from_csv(db, "./data/orders.csv")
    load_routes_from_csv(db, "./data/routes.csv")
