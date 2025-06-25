from sqlalchemy import Column, Integer, ForeignKey, JSON, TIMESTAMP
from app.database import Base

class OrderAudit(Base):
    __tablename__ = "order_audit"

    id_order_audit = Column(Integer, primary_key=True, index=True)
    id_order = Column(Integer, ForeignKey("order.id_order"))
    operation = Column(Integer)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(Integer)
    date = Column(TIMESTAMP)