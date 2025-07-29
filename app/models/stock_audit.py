from sqlalchemy import Column, String, Integer, JSON, TIMESTAMP, func
from app.database import Base
class StockAudit(Base):
    __tablename__ = "stock_audit"

    id_stock_audit = Column(Integer, primary_key=True, index=True)
    id_stock = Column(Integer)
    operation = Column(String)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(Integer)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)