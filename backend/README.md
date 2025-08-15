# Backend - FastAPI Application

This is the backend for the Delivery Driver Management & Route Optimization System, built with FastAPI.

## Features

-   **Data Loading**: Reads driver, order, and route data from CSV files.
-   **RESTful API**: Provides endpoints for managing drivers, orders, and routes.
-   **Route Optimization**: Assigns orders to drivers based on defined optimization rules and calculates KPIs.
-   **Simulation History**: Stores and retrieves past simulation runs.
-   **SQLite Database**: Uses SQLAlchemy ORM for data persistence.

## Setup and Run Locally

1.  **Navigate to the backend directory**:
    ```bash
    cd delivery-driver-system/backend
    ```

2.  **Create a Python virtual environment and activate it**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be available at `http://localhost:8000`.

## API Endpoints

FastAPI automatically generates interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

Here's a summary of the available endpoints:

### Drivers
-   `POST /drivers`: Create a new driver.
    -   **Request Body**: `DriverCreate` schema (e.g., `{"driver_id": "driver1", "name": "John Doe", "shift_hours_today": 8.0, "hours_worked_past_week": 40.0}`)
    -   **Response**: `Driver` schema
-   `GET /drivers`: Get all drivers.
    -   **Response**: List of `Driver` schemas
-   `GET /drivers/{driver_id}`: Get a single driver by ID.
    -   **Response**: `Driver` schema
-   `PUT /drivers/{driver_id}`: Update an existing driver.
    -   **Request Body**: `DriverUpdate` schema (partial update allowed, e.g., `{"name": "Jane Doe"}`)
    -   **Response**: `Driver` schema
-   `DELETE /drivers/{driver_id}`: Delete a driver.
    -   **Response**: `204 No Content`

### Orders
-   `POST /orders`: Create a new order.
    -   **Request Body**: `OrderCreate` schema (e.g., `{"order_id": "order1", "value": 150.75, "route_id": "routeA", "delivery_time": "2025-08-12T10:00:00"}`)
    -   **Response**: `Order` schema
-   `GET /orders`: Get all orders.
    -   **Response**: List of `Order` schemas
-   `GET /orders/{order_id}`: Get a single order by ID.
    -   **Response**: `Order` schema
-   `PUT /orders/{order_id}`: Update an existing order.
    -   **Request Body**: `OrderUpdate` schema (partial update allowed, e.g., `{"value": 160.0}`)
    -   **Response**: `Order` schema
-   `DELETE /orders/{order_id}`: Delete an order.
    -   **Response**: `204 No Content`

### Routes
-   `POST /routes`: Create a new route.
    -   **Request Body**: `RouteCreate` schema (e.g., `{"route_id": "routeA", "distance_km": 10.5, "traffic_level": "low", "base_time_minutes": 15}`)
    -   **Response**: `Route` schema
-   `GET /routes`: Get all routes.
    -   **Response**: List of `Route` schemas
-   `GET /routes/{route_id}`: Get a single route by ID.
    -   **Response**: `Route` schema
-   `PUT /routes/{route_id}`: Update an existing route.
    -   **Request Body**: `RouteUpdate` schema (partial update allowed, e.g., `{"traffic_level": "high"}`)
    -   **Response**: `Route` schema
-   `DELETE /routes/{route_id}`: Delete a route.
    -   **Response**: `204 No Content`

### Optimization
-   `POST /assign_orders`: Run the optimization algorithm to assign orders to drivers and calculate KPIs.
    -   **Request Body**: `SimulationInput` schema (e.g., `{"num_available_drivers": 5, "route_start_time": "09:00", "max_hours_per_driver_per_day": 8.0}`). All fields are optional.
    -   **Response**: JSON object containing `message`, `assignments` (list of assigned orders), and `kpis` (object with calculated KPIs like `total_profit`, `efficiency_score`, etc.).
-   `GET /optimized_schedule`: Get the current optimized assignment with ETA and the last calculated KPIs.
    -   **Response**: `OptimizedScheduleResponse` schema (object containing `schedule` and `kpis`).

### Simulation History
-   `GET /simulation_history`: Get a list of past simulation runs with their inputs and calculated KPIs.
    -   **Response**: List of `SimulationRun` schemas.

## Testing

To run the unit tests, navigate to the `backend` directory and run:

```bash
pytest
```

## Data Files

CSV data files (`drivers.csv`, `orders.csv`, `routes.csv`) are located in the `data/` directory. These files are loaded into the SQLite database on application startup.