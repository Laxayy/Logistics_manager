from typing import List, Dict, Any
from models import Truck, RouteCluster, Order

def assign_routes_to_fleet(clusters: List[RouteCluster], fleet: List[Truck]) -> Dict[str, Any]:
    sorted_clusters = sorted(clusters, key=lambda c: c.total_route_distance, reverse=True)

    assignments = {truck.id: [] for truck in fleet}
    failed_orders = []

    for cluster in sorted_clusters:
        assigned = False
        
        for truck in fleet:
            remaining_distance = truck.max_daily_distance - truck.distance_used
            
            if cluster.total_route_distance <= remaining_distance:
                assignments[truck.id].append(cluster)
                truck.distance_used += cluster.total_route_distance
                
                for order in cluster.orders:
                    order.is_assigned = True
                    
                assigned = True
                break  
        
        if not assigned:
            for order in cluster.orders:
                order.priority += 1  
                failed_orders.append(order)

    return {
        "fleet_assignments": assignments,
        "failed_orders": failed_orders
    }