from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Store(Base):
    __tablename__ = "store"

    id_store = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cnpj = Column(String, nullable=False, unique=True)
    creation_date = Column(Date, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False)
    image = Column(String)
    created_by = Column(Integer, nullable=False)