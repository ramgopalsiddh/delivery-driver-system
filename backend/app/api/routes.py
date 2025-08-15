from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.crud import route as crud_route
from app.schemas.route import Route, RouteCreate, RouteUpdate # Updated import
from app.core.database import get_db

router = APIRouter()

@router.post("/routes", response_model=Route, status_code=status.HTTP_201_CREATED)
def create_route(route: RouteCreate, db: Session = Depends(get_db)):
    db_route = crud_route.get_route(db, route_id=route.route_id)
    if db_route:
        raise HTTPException(status_code=400, detail="Route with this ID already registered")
    return crud_route.create_route(db=db, route=route)

@router.get("/routes", response_model=List[Route])
def read_routes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    routes = crud_route.get_routes(db, skip=skip, limit=limit)
    return routes

@router.get("/routes/{route_id}", response_model=Route)
def read_route(route_id: str, db: Session = Depends(get_db)):
    db_route = crud_route.get_route(db, route_id=route_id)
    if db_route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return db_route

@router.put("/routes/{route_id}", response_model=Route)
def update_route(route_id: str, route: RouteUpdate, db: Session = Depends(get_db)):
    db_route = crud_route.update_route(db, route_id, route.model_dump(exclude_unset=True))
    if db_route is None:
        raise HTTPException(status_code=404, detail="Route not found")
    return db_route

@router.delete("/routes/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(route_id: str, db: Session = Depends(get_db)):
    success = crud_route.delete_route(db, route_id)
    if not success:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Route deleted successfully"}
