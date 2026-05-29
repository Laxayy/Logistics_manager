from sqlalchemy.orm import Session
from typing import List
from models import Order
from db_models import DBOrder

def merge_and_prioritize_orders(db: Session, incoming_orders: List[Order]) -> List[Order]:
    
    failed_db_orders = db.query(DBOrder).filter(DBOrder.is_assigned == False).all()
    
    merged_orders = []
    existing_ids = set()

    
    for db_order in failed_db_orders:
        merged_orders.append(Order(
            id=db_order.id,
            lat=db_order.lat,
            lng=db_order.lng,
            weight=db_order.weight,
            priority=db_order.priority, 
            is_assigned=False
        ))
        existing_ids.add(db_order.id)
    
    
    for inc_order in incoming_orders:
        if inc_order.id not in existing_ids:
            new_db_order = DBOrder(
                id=inc_order.id, lat=inc_order.lat, lng=inc_order.lng, 
                weight=inc_order.weight, priority=inc_order.priority, is_assigned=False
            )
            db.add(new_db_order)
            merged_orders.append(inc_order)
    
    db.commit()
    
    return sorted(merged_orders, key=lambda x: x.priority, reverse=True)

def update_dispatch_results(db: Session, final_manifest: dict):
    
    for truck_id, clusters in final_manifest.get("fleet_assignments", {}).items():
        for cluster in clusters:
            for order in cluster.orders: 
                db_order = db.query(DBOrder).filter(DBOrder.id == order.id).first()
                if db_order:
                    db_order.is_assigned = True
    
    
    for failed_order in final_manifest.get("failed_orders", []):
        db_order = db.query(DBOrder).filter(DBOrder.id == failed_order.id).first()
        if db_order:
            db_order.priority = failed_order.priority 
            db_order.is_assigned = False
    
    db.commit()