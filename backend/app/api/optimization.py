from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.services.optimizer import Optimizer
from app.core.database import get_db
from app.schemas.assignment import Assignment
from app.schemas.optimization import SimulationInput, OptimizedScheduleResponse # Updated import

router = APIRouter()

@router.post("/assign_orders")
def assign_orders(simulation_input: SimulationInput, db: Session = Depends(get_db)):
    optimizer = Optimizer(db)
    result = optimizer.assign_orders(simulation_input)
    return result

@router.get("/optimized_schedule", response_model=OptimizedScheduleResponse) # Updated response_model
def get_optimized_schedule(db: Session = Depends(get_db)):
    optimizer = Optimizer(db)
    schedule = optimizer.get_optimized_schedule()
    return schedule
