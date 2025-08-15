from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware # Added import

from app.core.database import engine, Base, get_db
from app.api import drivers, orders, routes, optimization, simulation_history # New import
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

app.include_router(drivers.router)
app.include_router(orders.router)
app.include_router(routes.router)
app.include_router(optimization.router)
app.include_router(simulation_history.router) # New router include

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Delivery Driver Management API"}
