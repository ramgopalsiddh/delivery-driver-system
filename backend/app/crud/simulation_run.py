from sqlalchemy.orm import Session
from app.models.simulation_run import SimulationRun
from app.schemas.simulation_run import SimulationRunCreate

def create_simulation_run(db: Session, simulation_run: SimulationRunCreate):
    db_simulation_run = SimulationRun(**simulation_run.model_dump())
    db.add(db_simulation_run)
    db.commit()
    db.refresh(db_simulation_run)
    return db_simulation_run

def get_simulation_runs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SimulationRun).offset(skip).limit(limit).all()
