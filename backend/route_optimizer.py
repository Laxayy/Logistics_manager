from typing import List, Tuple
from models import Order
import math

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    return math.hypot(lat1 - lat2, lng1 - lng2)

def optimize_route_sequence(orders: List[Order], warehouse_lat: float, warehouse_lng: float) -> Tuple[List[Order], float]:

    if not orders:
        return [], 0.0

    unvisited = orders.copy()
    sequenced_orders = []
    current_lat = warehouse_lat
    current_lng = warehouse_lng
    total_distance = 0.0

    while unvisited:

        nearest_order = None
        shortest_dist = float('inf')
        nearest_idx = -1
        for i, order in enumerate(unvisited):
            dist = calculate_distance(current_lat, current_lng, order.lat, order.lng)
            if dist < shortest_dist:
                shortest_dist = dist
                nearest_order = order
                nearest_idx = i

        sequenced_orders.append(nearest_order)
        unvisited.pop(nearest_idx)
        total_distance += shortest_dist      
        current_lat = nearest_order.lat
        current_lng = nearest_order.lng

    return_leg_distance = calculate_distance(current_lat, current_lng, warehouse_lat, warehouse_lng)
    total_distance += return_leg_distance

    return sequenced_orders, total_distance