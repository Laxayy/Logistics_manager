from sqlalchemy import Column, String, Float, Integer, Boolean
from database import Base

class DBOrder(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    lat = Column(Float)
    lng = Column(Float)
    weight = Column(Float)
    priority = Column(Integer, default=1)
    is_assigned = Column(Boolean, default=False)