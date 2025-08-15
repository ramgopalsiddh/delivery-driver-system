from sqlalchemy.orm import Session
from app.models.driver import Driver
from app.schemas.driver import DriverCreate

def get_driver(db: Session, driver_id: str):
    return db.query(Driver).filter(Driver.driver_id == driver_id).first()

def get_drivers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Driver).offset(skip).limit(limit).all()

def create_driver(db: Session, driver: DriverCreate):
    db_driver = Driver(**driver.model_dump())
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def create_or_update_driver(db: Session, driver: DriverCreate):
    db_driver = db.query(Driver).filter(Driver.driver_id == driver.driver_id).first()
    if db_driver:
        for key, value in driver.model_dump().items():
            setattr(db_driver, key, value)
        db.commit()
        db.refresh(db_driver)
        return db_driver
    else:
        return create_driver(db, driver)

def update_driver(db: Session, driver_id: str, driver_data: dict):
    db_driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if db_driver:
        for key, value in driver_data.items():
            setattr(db_driver, key, value)
        db.commit()
        db.refresh(db_driver)
        return db_driver
    return None

def delete_driver(db: Session, driver_id: str):
    db_driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()
    if db_driver:
        db.delete(db_driver)
        db.commit()
        return True
    return False
