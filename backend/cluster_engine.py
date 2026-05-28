import math
from typing import List
from models import Order, RouteCluster


#temporary distanvce , have to add street distacne later 
def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return math.hypot(lat1 - lat2, lng1 - lng2)

def generate_route_clusters(all_orders: List[Order], truck_max_weight: float, warehouse_lat: float, warehouse_lng: float) -> List[RouteCluster]:
    
    clusters = []
    cluster_counter = 1
    
    pending_orders = sorted(all_orders, key=lambda x: x.priority, reverse=True)

    while pending_orders:

        seed_order = pending_orders.pop(0) # starting node for this cluster 
        current_cluster_orders = [seed_order]
        current_weight = seed_order.weight
        
        dist_to_seed = _calculate_distance(warehouse_lat, warehouse_lng, seed_order.lat, seed_order.lng)
        current_distance = dist_to_seed * 2 
        
        last_node = seed_order

        while True:
            best_candidate_idx = -1
            best_extra_distance = float('inf')
            
            for i, candidate in enumerate(pending_orders):
                
                if current_weight + candidate.weight <= truck_max_weight:
                    
                    dist_to_candidate = _calculate_distance(last_node.lat, last_node.lng, candidate.lat, candidate.lng)
                    dist_back_to_wh = _calculate_distance(candidate.lat, candidate.lng, warehouse_lat, warehouse_lng)
                    dist_saved = _calculate_distance(last_node.lat, last_node.lng, warehouse_lat, warehouse_lng)
                    
                    extra_distance = dist_to_candidate + dist_back_to_wh - dist_saved
                    
                    if extra_distance < best_extra_distance:
                        best_extra_distance = extra_distance
                        best_candidate_idx = i
            
            if best_candidate_idx != -1:
                winning_order = pending_orders.pop(best_candidate_idx)
                current_cluster_orders.append(winning_order)
                current_weight += winning_order.weight
                current_distance += best_extra_distance
                last_node = winning_order 
            else:

                break 
                
        clusters.append(RouteCluster(
            cluster_id=f"ROUTE-{cluster_counter}",
            orders=current_cluster_orders,
            total_weight=current_weight,
            total_route_distance=current_distance  
        ))
        cluster_counter += 1

    return clusters