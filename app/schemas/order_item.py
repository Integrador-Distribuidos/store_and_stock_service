from pydantic import BaseModel
from datetime import date

class OrderItemCreate(BaseModel):
    id_product: int
    id_stock: int
    unit_price: float
    quantity: int
    subtotal: float
    creation_date: date
    date_change: date

class OrderItemOut(OrderItemCreate):
    id_order_item: int
    id_order: int

    class Config:
        orm_mode = True
