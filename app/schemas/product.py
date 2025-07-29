from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List, Dict, Any
# ---------- PRODUCT ----------
class ProductStockInfo(BaseModel):
    id_stock: int
    quantity: int

class ProductStockOutInfo(BaseModel):
    id_product: int
    name: str
    quantity: int


class ProductCreate(BaseModel):
    name: str
    image: str
    description: str
    price: float
    sku: str
    category: str
    quantity: Optional[int] = []
    creation_date: date

class ProductOut(BaseModel):
    id_product: int
    name: str
    image: Optional[str] = []
    description: str
    price: float
    sku: str
    category: str
    quantity: Optional[int] = []
    stocks: Optional[List[ProductStockInfo]] = []
    creation_date: date

    class Config:
        orm_mode = True


class ProductUpdate(BaseModel):
    name: Optional[str]
    image: Optional[str]
    description: Optional[str]
    price: Optional[float]
    sku: Optional[str]
    category: Optional[str]
    quantity: Optional[int]
    creation_date: Optional[date]
    stocks: Optional[List[ProductStockInfo]]=None

    class Config:
        orm_mode = True


class ProductStock(BaseModel):
    id_product: int
    id_stock: int
    quantity: int
    last_update_date: date

class ProductStockOut(BaseModel):
    id_productstock: int
    id_product: int
    id_stock: int
    quantity: int
    last_update_date: date



class ProductAuditOut(BaseModel):
    id_movement_audit: int
    id_movement: int
    operation: str
    old_data: Optional[dict[str, Any]]
    new_data: Optional[dict[str, Any]]
    changed_by: int
    date: datetime

    class Config:
        orm_mode = True