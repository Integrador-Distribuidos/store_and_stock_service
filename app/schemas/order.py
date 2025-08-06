from pydantic import BaseModel
from datetime import date
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    DRAFT = "draft"
    COMPLETED = "completed"
    PAID = "paid"

class OrderCreate(BaseModel):
    id_user: int
    id_store: int
    status: OrderStatus = OrderStatus.DRAFT
    order_date: Optional[date] = None
    total_value: float = 0.0
    creation_date: date


class OrderItemPatch(BaseModel):
    id_product: Optional[int] = None
    id_stock: Optional[int] = None
    unit_price: Optional[float] = None
    quantity: Optional[int] = None
    subtotal: Optional[float] = None
    creation_date: Optional[date] = None
    date_change: Optional[date] = None

class OrderOut(OrderCreate):
    id_order: int

    class Config:
        orm_mode = True
