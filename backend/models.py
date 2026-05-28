from pydantic import BaseModel
from typing import List, Optional


class Order(BaseModel):
    id: str
    lat: float
    lng: float
    weight: float
    priority: int = 1            
    is_assigned: bool = False   

class Truck(BaseModel):
    id: str
    max_weight_capacity: float
    max_daily_distance: float
    distance_used: float = 0.0   

class RouteCluster(BaseModel):
    cluster_id: str
    orders: List[Order]
    total_weight: float
    
    def is_valid(self, max_capacity: float) -> bool:
        return self.total_weight <= max_capacity