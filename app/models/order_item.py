from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class OrderItem(Base):
    __tablename__ = "order_item"

    id_order_item = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey("order.id_order"), nullable=False)
    id_product = Column(Integer, nullable=False)
    id_stock = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    subtotal = Column(Float, nullable=False)
    creation_date = Column(Date, nullable=False)
    date_change = Column(Date, nullable=False)

    order = relationship("Order", back_populates="items")
