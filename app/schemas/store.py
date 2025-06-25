from pydantic import BaseModel, EmailStr
from datetime import date

class StoreCreate(BaseModel):
    name: str
    cnpj: str
    city: str
    uf: str
    zip_code: str
    address: str
    creation_date: date
    email: str
    phone_number: str

class StoreOut(StoreCreate):
    id_store: int

    class Config:
        orm_mode = True
