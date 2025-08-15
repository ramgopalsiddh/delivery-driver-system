from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import simulation_run as crud_simulation_run
from app.schemas.simulation_run import SimulationRun
from app.core.database import get_db

router = APIRouter()

@router.get("/simulation_history", response_model=List[SimulationRun])
def get_simulation_history(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    history = crud_simulation_run.get_simulation_runs(db, skip=skip, limit=limit)
    return history
