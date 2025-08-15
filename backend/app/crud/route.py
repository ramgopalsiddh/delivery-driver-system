from sqlalchemy.orm import Session
from app.models.route import Route
from app.schemas.route import RouteCreate

def get_route(db: Session, route_id: str):
    return db.query(Route).filter(Route.route_id == route_id).first()

def get_routes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Route).offset(skip).limit(limit).all()

def create_route(db: Session, route: RouteCreate):
    db_route = Route(**route.model_dump())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route

def create_or_update_route(db: Session, route: RouteCreate):
    db_route = db.query(Route).filter(Route.route_id == route.route_id).first()
    if db_route:
        for key, value in route.model_dump().items():
            setattr(db_route, key, value)
        db.commit()
        db.refresh(db_route)
        return db_route
    else:
        return create_route(db, route)

def update_route(db: Session, route_id: str, route_data: dict):
    db_route = db.query(Route).filter(Route.route_id == route_id).first()
    if db_route:
        for key, value in route_data.items():
            setattr(db_route, key, value)
        db.commit()
        db.refresh(db_route)
        return db_route
    return None

def delete_route(db: Session, route_id: str):
    db_route = db.query(Route).filter(Route.route_id == route_id).first()
    if db_route:
        db.delete(db_route)
        db.commit()
        return True
    return False
