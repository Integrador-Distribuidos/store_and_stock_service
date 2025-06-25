from pydantic import BaseModel
from datetime import date

class OrderCreate(BaseModel):
    id_user: int
    id_store: int
    status: str
    order_date: date  
    total_value: float
    creation_date: date

class OrderOut(OrderCreate):
    id_order: int

    class Config:
        orm_mode = True
