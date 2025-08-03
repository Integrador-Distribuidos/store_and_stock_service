from pydantic import BaseModel
from datetime import date
from typing import Optional, List
class ProductStockOutInfo(BaseModel):
    id_product: int
    name: str
    quantity: int
# ---------- STOCK ----------
class StockCreate(BaseModel):
    id_store: int
    name: str
    city: str
    uf: str
    zip_code: str
    address: str
    creation_date: date

class StockOut(StockCreate):
    id_stock: int
    products: Optional[List[ProductStockOutInfo]] = []

    class Config:
        orm_mode = True