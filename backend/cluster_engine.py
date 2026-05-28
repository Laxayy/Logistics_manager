import math
from typing import List
from models import Order, RouteCluster

from route_optimizer import optimize_route_sequence

def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return math.hypot(lat1 - lat2, lng1 - lng2)

def generate_route_clusters(all_orders: List[Order], truck_max_weight: float, warehouse_lat: float, warehouse_lng: float) -> List[RouteCluster]:
    clusters = []
    cluster_counter = 1
    
    pending_orders = sorted(all_orders, key=lambda x: x.priority, reverse=True)

    while pending_orders:
        seed_order = pending_orders.pop(0) 
        current_cluster_orders = [seed_order]
        current_weight = seed_order.weight
        last_node = seed_order

        while True:
            best_candidate_idx = -1
            best_extra_distance = float('inf')
            
            for i, candidate in enumerate(pending_orders):
                if current_weight + candidate.weight <= truck_max_weight:
                    dist_to_candidate = _calculate_distance(last_node.lat, last_node.lng, candidate.lat, candidate.lng)
                    
                    if dist_to_candidate < best_extra_distance:
                        best_extra_distance = dist_to_candidate
                        best_candidate_idx = i
            
            if best_candidate_idx != -1:
                winning_order = pending_orders.pop(best_candidate_idx)
                current_cluster_orders.append(winning_order)
                current_weight += winning_order.weight
                last_node = winning_order 
            else:
                break 
                
        sequenced_orders, true_route_distance = optimize_route_sequence(
            orders=current_cluster_orders,
            warehouse_lat=warehouse_lat,
            warehouse_lng=warehouse_lng
        )

        clusters.append(RouteCluster(
            cluster_id=f"ROUTE-{cluster_counter}",
            orders=sequenced_orders,
            total_weight=current_weight,
            total_route_distance=true_route_distance  
        ))
        cluster_counter += 1

    return clusters