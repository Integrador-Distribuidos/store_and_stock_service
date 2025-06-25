from sqlalchemy import Column, Integer, String, JSON, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class OrderItemAudit(Base):
    __tablename__ = "order_item_audit"

    id_order_item_audit = Column(Integer, primary_key=True, index=True)
    id_order_item = Column(Integer, ForeignKey("order_item.id_order_item"), nullable=False)
    operation = Column(String, nullable=False)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, nullable=False)

    order_item = relationship("OrderItem", backref="audits")
