from pydantic import BaseModel
from datetime import date
from typing import Optional, List
class ProductStockOutInfo(BaseModel):
    id_product: int
    name: str
    quantity: int
# ---------- STOCK ----------
class StockCreate(BaseModel):
    name: str
    city: str
    uf: str
    zip_code: str
    address: str
    creation_date: date

class StockOut(BaseModel):
    id_stock: int
    name: Optional[str] = None
    city: Optional[str] = None
    uf: Optional[str] = None
    zip_code: Optional[str] = None
    address: Optional[str] = None
    creation_date: Optional[date] = None
    products: Optional[List[ProductStockOutInfo]] = []

    class Config:
        orm_mode = True