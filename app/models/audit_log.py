from sqlalchemy import Column, Integer, JSON, String, DateTime
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    table_name = Column(String, nullable=False)
    operation = Column(String, nullable=False)  # INSERT, UPDATE, DELETE
    old_data = Column(JSON)
    new_data = Column(JSON)
    user = Column(Integer)  # opcional: ID do usuário, IP etc.
    timestamp = Column(DateTime, default=datetime.utcnow)