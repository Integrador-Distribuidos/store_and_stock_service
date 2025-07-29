from sqlalchemy import Column, Integer, JSON,  TIMESTAMP, func
from app.database import Base
class StockMovementAudit(Base):
    __tablename__ = "stock_movement_audit"

    id_movement_audit = Column(Integer, primary_key=True, index=True)
    id_movement = Column(Integer, nullable=False)
    operation = Column(Integer)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(Integer)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)