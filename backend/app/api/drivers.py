from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import driver as crud_driver
from app.schemas.driver import Driver, DriverCreate, DriverUpdate # Updated import
from app.core.database import get_db

router = APIRouter()

@router.post("/drivers", response_model=Driver, status_code=status.HTTP_201_CREATED)
def create_driver(driver: DriverCreate, db: Session = Depends(get_db)):
    db_driver = crud_driver.get_driver(db, driver_id=driver.driver_id)
    if db_driver:
        raise HTTPException(status_code=400, detail="Driver with this ID already registered")
    return crud_driver.create_driver(db=db, driver=driver)

@router.get("/drivers", response_model=List[Driver])
def read_drivers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    drivers = crud_driver.get_drivers(db, skip=skip, limit=limit)
    return drivers

@router.get("/drivers/{driver_id}", response_model=Driver)
def read_driver(driver_id: str, db: Session = Depends(get_db)):
    db_driver = crud_driver.get_driver(db, driver_id=driver_id)
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

@router.put("/drivers/{driver_id}", response_model=Driver)
def update_driver(driver_id: str, driver: DriverUpdate, db: Session = Depends(get_db)):
    db_driver = crud_driver.update_driver(db, driver_id, driver.model_dump(exclude_unset=True))
    if db_driver is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_driver

@router.delete("/drivers/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: str, db: Session = Depends(get_db)):
    success = crud_driver.delete_driver(db, driver_id)
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": "Driver deleted successfully"}
