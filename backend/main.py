from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Order, Truck


from cluster_engine import generate_route_clusters
from dispatcher import assign_routes_to_fleet
from pydantic import BaseModel

app = FastAPI(title="Logistics Dispatch API")

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
def execute_dispatch(payload: DispatchPayload):
    
    standard_truck_weight = payload.trucks[0].max_weight_capacity if payload.trucks else 1000.0
    
    generated_routes = generate_route_clusters(
        all_orders=payload.orders,
        truck_max_weight=standard_truck_weight,
        warehouse_lat=payload.warehouse_lat,
        warehouse_lng=payload.warehouse_lng
    )
    
    final_manifest = assign_routes_to_fleet(
        clusters=generated_routes,
        fleet=payload.trucks
    )
    return final_manifest


@app.get("/")
def health_check():
    return {"status": "Engine is running perfectly"}