from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    cnpj: str
    creation_date: date
    email: str
    phone_number: str

class StoreOut(StoreCreate):
    id_store: int
    image: Optional[str] = []

    class Config:
        orm_mode = True
