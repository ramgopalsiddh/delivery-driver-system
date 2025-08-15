from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware # Added import

from app.core.database import engine, Base, get_db
from app.api import drivers, orders, routes, optimization, simulation_history, auth # New import
from app.core.security import get_current_user # New import
import app.models.user # Ensure User model is registered with Base.metadata
from app.services.data_loader import load_all_data

app = FastAPI(
    title="Delivery Driver Management API",
    description="API for managing delivery drivers, orders, and route optimization.",
    version="1.0.0",
)

# Added CORS middleware
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Load initial data from CSVs
    db = next(get_db())
    load_all_data(db)
    db.close()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(drivers.router, dependencies=[Depends(get_current_user)])
app.include_router(orders.router, dependencies=[Depends(get_current_user)])
app.include_router(routes.router, dependencies=[Depends(get_current_user)])
app.include_router(optimization.router, dependencies=[Depends(get_current_user)])
app.include_router(simulation_history.router, dependencies=[Depends(get_current_user)]) # New router include

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Delivery Driver Management API"}
