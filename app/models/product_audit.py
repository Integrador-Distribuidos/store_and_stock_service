from sqlalchemy import Column, Integer, JSON, TIMESTAMP, String, func
from app.database import Base
class ProductAudit(Base):
    __tablename__ = "product_audit"

    id_product_audit = Column(Integer, primary_key=True, index=True)
    id_product = Column(Integer)
    operation = Column(String)
    old_data = Column(JSON)
    new_data = Column(JSON)
    changed_by = Column(Integer)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)