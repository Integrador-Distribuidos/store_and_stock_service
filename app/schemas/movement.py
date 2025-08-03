from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict

class StockMovementCreate(BaseModel):
    id_product: int
    id_stock_origin: Optional[int]
    id_stock_destination: Optional[int]
    quantity: int
    observation: Optional[str] = None
    creation_date: date

class StockMovementOut(StockMovementCreate):
    id_movement: int

    class Config:
        orm_mode = True