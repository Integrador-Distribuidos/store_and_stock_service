from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "order"

    id_order = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, nullable=False)
    id_store = Column(Integer, ForeignKey("store.id_store"), nullable=False)
    status = Column(String, nullable=False)
    order_date = Column(Date, nullable=False)
    total_value = Column(Float, nullable=False)
    creation_date = Column(Date, nullable=False)
