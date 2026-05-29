from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models import Order, Truck
from cluster_engine import generate_route_clusters
from dispatcher import assign_routes_to_fleet
from database import engine, Base, get_db
from order_manager import merge_and_prioritize_orders, update_dispatch_results

# Instructs SQLAlchemy to generate the SQLite tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NEBULA Logistics Dispatch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DispatchPayload(BaseModel):
    orders: List[Order]
    trucks: List[Truck]
    warehouse_lat: float
    warehouse_lng: float

@app.post("/api/run-dispatch")
def execute_dispatch(payload: DispatchPayload, db: Session = Depends(get_db)):
    
    # Execute Phase 1: State Retrieval and Prioritization
    active_orders = merge_and_prioritize_orders(db, payload.orders)
    
    standard_truck_weight = payload.trucks[0].max_weight_capacity if payload.trucks else 1000.0
    
    # Execute Phase 2 & 3: Spatial Clustering and TSP Routing
    generated_routes = generate_route_clusters(
        all_orders=active_orders,
        truck_max_weight=standard_truck_weight,
        warehouse_lat=payload.warehouse_lat,
        warehouse_lng=payload.warehouse_lng
    )
    
    # Execute Phase 4: Fleet Assignment and Capacity Constraints
    final_manifest = assign_routes_to_fleet(
        clusters=generated_routes,
        fleet=payload.trucks
    )
    
    # Execute Phase 5: State Persistence
    update_dispatch_results(db, final_manifest)
    
    return final_manifest

@app.get("/")
def health_check():
    return {"status": "Engine is running perfectly"}