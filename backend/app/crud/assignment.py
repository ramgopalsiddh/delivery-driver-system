from sqlalchemy.orm import Session
from app.models.assignment import Assignment
from app.schemas.assignment import AssignmentCreate

def get_assignment(db: Session, order_id: str):
    return db.query(Assignment).filter(Assignment.order_id == order_id).first()

def get_assignments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Assignment).offset(skip).limit(limit).all()

def create_assignment(db: Session, assignment: AssignmentCreate):
    db_assignment = Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit() # This commits the transaction
    db.refresh(db_assignment)
    print(f"DEBUG: Created and committed assignment for order {db_assignment.order_id}") # DEBUG
    return db_assignment

def delete_all_assignments(db: Session):
    db.query(Assignment).delete()
    db.commit()
