from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
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
    creation_date: date

class ProductOut(BaseModel):
    id_product: int
    name: str
    image: str
    description: str
    price: float
    sku: str
    category: str
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