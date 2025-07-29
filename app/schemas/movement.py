from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict




class StockMovementCreate(BaseModel):
    id_product: int
    id_stock_origin: int
    id_stock_destination: int
    quantity: int
    observation: Optional[str] = None
    movement_type: str  
    creation_date: date

class StockMovementOut(BaseModel):
    id_movement: int
    id_product: int
    id_stock_origin: Optional[int]
    id_stock_destination: Optional[int]
    quantity: int
    observation: Optional[str]
    movement_type: str
    creation_date: date

    class Config:
        orm_mode = True



class StockMovementAuditOut(BaseModel):
    id_movement_audit: int
    id_movement: int
    operation: str
    data: Dict
    changed_by: int
    date: datetime

    class Config:
        orm_mode = True