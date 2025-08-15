from sqlalchemy.orm import Session
from app.models.driver import Driver
from app.models.order import Order
from app.models.route import Route
from app.crud import assignment as crud_assignment
from app.crud import order as crud_order
from app.crud import route as crud_route
from app.crud import driver as crud_driver
from app.crud import simulation_run as crud_simulation_run # New import
from app.schemas.assignment import AssignmentCreate
from app.schemas.simulation_run import SimulationRunCreate # New import
from app.schemas.optimization import SimulationInput # New import
from datetime import datetime, timedelta

# Company Rule Constants
LATE_DELIVERY_PENALTY = 50  # ₹50
FATIGUE_SPEED_DECREASE_FACTOR = 0.30 # 30% decrease
HIGH_VALUE_BONUS_THRESHOLD = 1000 # ₹1000
HIGH_VALUE_BONUS_PERCENTAGE = 0.10 # 10%
BASE_FUEL_COST_PER_KM = 5 # ₹5/km
HIGH_TRAFFIC_FUEL_SURCHARGE_PER_KM = 2 # ₹2/km

class Optimizer:
    def __init__(self, db: Session):
        self.db = db
        self.avg_speed_kmh = 30  # Default average speed in km/h
        self.traffic_factors = {
            "low": 0.1,   # 10% increase in base time
            "medium": 0.3, # 30% increase
            "high": 0.6   # 60% increase
        }
        self._last_kpis = None # New: Store last calculated KPIs

    def _calculate_estimated_delivery_time(self, route: Route, driver: Driver) -> timedelta:
        # estimated_delivery_time = base_time_minutes + traffic_factor + (distance_km / avg_speed)*60
        traffic_multiplier = 1 + self.traffic_factors.get(route.traffic_level.lower(), 0.2) # Default 20% if not found
        travel_time_hours = route.distance_km / self.avg_speed_kmh
        travel_time_minutes = travel_time_hours * 60
        
        estimated_minutes = route.base_time_minutes * traffic_multiplier + travel_time_minutes

        # Driver Fatigue Rule: If a driver works >8 hours in a day, their delivery speed decreases by 30%
        # Simplified: Check current shift_hours_today or average past_week_hours
        if driver.shift_hours_today > 8 or (driver.hours_worked_past_week / 7) > 8:
            estimated_minutes *= (1 + FATIGUE_SPEED_DECREASE_FACTOR)

        return timedelta(minutes=estimated_minutes)

    def _calculate_late_delivery_penalty(self, estimated_delivery_time: datetime, order_delivery_time: datetime) -> float:
        # Rule 1: If delivery time > (base route time + 10 minutes), apply ₹50 penalty
        # Assuming order_delivery_time is the customer's requested delivery time
        # and estimated_delivery_time is what we calculated.
        # The rule states "base route time + 10 minutes", which is a bit ambiguous with our estimated_delivery_time.
        # I will interpret this as: if our estimated delivery time is more than 10 minutes past the customer's requested delivery time.
        if estimated_delivery_time > order_delivery_time + timedelta(minutes=10):
            return LATE_DELIVERY_PENALTY
        return 0.0

    def _calculate_high_value_bonus(self, order_value: float, is_on_time: bool) -> float:
        # Rule 3: If order value > ₹1000 AND delivered on time → add 10% bonus to order profit.
        if order_value > HIGH_VALUE_BONUS_THRESHOLD and is_on_time:
            return order_value * HIGH_VALUE_BONUS_PERCENTAGE
        return 0.0

    def _calculate_fuel_cost(self, route: Route) -> float:
        # Rule 4: Fuel Cost Calculation
        # Base cost: ₹5/km per route
        # If traffic level is "High" → +₹2/km fuel surcharge
        cost = route.distance_km * BASE_FUEL_COST_PER_KM
        if route.traffic_level.lower() == "high":
            cost += route.distance_km * HIGH_TRAFFIC_FUEL_SURCHARGE_PER_KM
        return cost

    def _calculate_order_profit(self, order: Order, route: Route, estimated_delivery_time: datetime) -> float:
        # Rule 5: Overall Profit for an order
        # Sum of (order value + bonus – penalties – fuel cost)
        is_on_time = estimated_delivery_time <= order.delivery_time # Delivered on or before requested time
        
        penalty = self._calculate_late_delivery_penalty(estimated_delivery_time, order.delivery_time)
        bonus = self._calculate_high_value_bonus(order.value, is_on_time)
        fuel_cost = self._calculate_fuel_cost(route)

        profit = order.value + bonus - penalty - fuel_cost
        return profit

    def _score_driver(self, driver: Driver, current_workload_minutes: float) -> float:
        # Lower score is better (prefer drivers with less work)
        score = (
            driver.shift_hours_today * 60  # Convert to minutes
            + driver.hours_worked_past_week * 60 / 7 # Average daily hours from past week
            + current_workload_minutes # Add current assigned workload
        )
        return score

    def assign_orders(self, simulation_input: SimulationInput):
        # Input validation
        if simulation_input.num_available_drivers is not None and simulation_input.num_available_drivers <= 0:
            raise HTTPException(status_code=400, detail="Number of available drivers must be positive.")
        if simulation_input.max_hours_per_driver_per_day is not None and simulation_input.max_hours_per_driver_per_day < 0:
            raise HTTPException(status_code=400, detail="Max hours per driver per day cannot be negative.")

        # Clear previous assignments
        crud_assignment.delete_all_assignments(self.db)

        # Unassign all orders
        all_orders = self.db.query(Order).all()
        for order in all_orders:
            order.assigned_driver_id = None
        self.db.commit()

        drivers = self.db.query(Driver).all()
        # Filter drivers based on num_available_drivers input
        if simulation_input.num_available_drivers is not None:
            drivers = drivers[:simulation_input.num_available_drivers]

        orders = self.db.query(Order).filter(Order.assigned_driver_id == None).all()
        print(f"DEBUG: Number of unassigned orders fetched: {len(orders)}") # DEBUG
        routes = {r.route_id: r for r in self.db.query(Route).all()}

        # Initialize KPI accumulators
        total_profit = 0.0
        total_deliveries = 0
        on_time_deliveries = 0
        total_fuel_cost = 0.0
        total_penalties = 0.0
        total_bonuses = 0.0

        # Initialize driver workloads
        driver_workloads = {driver.driver_id: 0.0 for driver in drivers}
        driver_assigned_orders = {driver.driver_id: [] for driver in drivers}

        # Sort orders by delivery time (earliest first) to prioritize
        orders.sort(key=lambda o: o.delivery_time)

        for order in orders:
            best_driver = None
            min_score = float('inf')

            route = routes.get(order.route_id)
            if not route:
                print(f"Warning: Route {order.route_id} not found for order {order.order_id}")
                continue

            # Pass driver to calculate_estimated_delivery_time for fatigue rule
            for driver in drivers:
                estimated_travel_time = self._calculate_estimated_delivery_time(route, driver)
                current_workload = driver_workloads[driver.driver_id]
                
                # Calculate potential new workload if this order is assigned
                potential_workload = current_workload + estimated_travel_time.total_seconds() / 60 # Convert timedelta to minutes

                # Max hours per driver per day constraint
                if simulation_input.max_hours_per_driver_per_day is not None and \
                   (driver.shift_hours_today + (potential_workload / 60)) > simulation_input.max_hours_per_driver_per_day:
                    continue # Skip this driver if they exceed max hours

                score = self._score_driver(driver, potential_workload)

                if score < min_score:
                    min_score = score
                    best_driver = driver
            
            if best_driver:
                print(f"DEBUG: Assigning order {order.order_id} to driver {best_driver.driver_id}") # DEBUG
                # Assign order to the best driver
                crud_order.assign_order_to_driver(self.db, order.order_id, best_driver.driver_id)
                
                # Record assignment
                assigned_at = datetime.now()
                # Use route_start_time if provided
                if simulation_input.route_start_time:
                    try:
                        start_time_obj = datetime.strptime(simulation_input.route_start_time, '%H:%M').time()
                        assigned_at = datetime.combine(assigned_at.date(), start_time_obj)
                    except ValueError:
                        print(f"Warning: Invalid route_start_time format: {simulation_input.route_start_time}")

                # Recalculate estimated_delivery_time with the chosen best_driver
                final_estimated_travel_time = self._calculate_estimated_delivery_time(route, best_driver)
                estimated_delivery_time_for_order = assigned_at + final_estimated_travel_time

                assignment_data = AssignmentCreate(
                    order_id=order.order_id,
                    driver_id=best_driver.driver_id,
                    estimated_delivery_time=estimated_delivery_time_for_order,
                    assigned_at=assigned_at
                )
                crud_assignment.create_assignment(self.db, assignment_data)

                # Update driver's workload
                driver_workloads[best_driver.driver_id] += final_estimated_travel_time.total_seconds() / 60
                driver_assigned_orders[best_driver.driver_id].append(order.order_id)

                # Calculate KPIs for this order
                is_on_time = estimated_delivery_time_for_order <= order.delivery_time
                penalty = self._calculate_late_delivery_penalty(estimated_delivery_time_for_order, order.delivery_time)
                bonus = self._calculate_high_value_bonus(order.value, is_on_time)
                fuel_cost = self._calculate_fuel_cost(route)
                order_profit = self._calculate_order_profit(order, route, estimated_delivery_time_for_order)

                total_profit += order_profit
                total_deliveries += 1
                if is_on_time:
                    on_time_deliveries += 1
                total_fuel_cost += fuel_cost
                total_penalties += penalty
                total_bonuses += bonus

        efficiency_score = (on_time_deliveries / total_deliveries) * 100 if total_deliveries > 0 else 0.0

        kpis_data = {
            "total_profit": total_profit,
            "efficiency_score": efficiency_score,
            "total_deliveries": total_deliveries,
            "on_time_deliveries": on_time_deliveries,
            "late_deliveries": total_deliveries - on_time_deliveries,
            "total_fuel_cost": total_fuel_cost,
            "total_penalties": total_penalties,
            "total_bonuses": total_bonuses
        }
        self._last_kpis = kpis_data # Store the last calculated KPIs

        # Save simulation run history
        simulation_run_data = SimulationRunCreate(
            timestamp=datetime.now(),
            num_available_drivers=simulation_input.num_available_drivers,
            route_start_time=simulation_input.route_start_time,
            max_hours_per_driver_per_day=simulation_input.max_hours_per_driver_per_day,
            **kpis_data
        )
        crud_simulation_run.create_simulation_run(self.db, simulation_run_data)

        print(f"DEBUG: Total assignments created in assign_orders: {len(crud_assignment.get_assignments(self.db))}") # DEBUG
        return {
            "message": "Orders assigned successfully",
            "assignments": driver_assigned_orders,
            "kpis": kpis_data
        }

    def get_optimized_schedule(self):
        assignments = self.db.query(crud_assignment.Assignment).all()
        print(f"DEBUG: Number of assignments fetched in get_optimized_schedule: {len(assignments)}") # DEBUG
        schedule = []
        for assignment in assignments:
            order = crud_order.get_order(self.db, assignment.order_id)
            driver = crud_driver.get_driver(self.db, assignment.driver_id)
            if order and driver:
                schedule.append({
                    "order_id": order.order_id,
                    "driver_name": driver.name,
                    "estimated_delivery_time": assignment.estimated_delivery_time.isoformat(),
                    "assigned_at": assignment.assigned_at.isoformat()
                })
        
        return {"schedule": schedule, "kpis": self._last_kpis}
