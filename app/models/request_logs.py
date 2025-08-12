from app.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
# Modelo para armazenar os logs
class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True, comment="Identificador único do log")
    method = Column(String, nullable=False, comment="Método HTTP da requisição")
    path = Column(String, nullable=False, comment="Caminho da URL requisitada")
    status_code = Column(Integer, nullable=False, comment="Código HTTP de resposta")
    process_time_ms = Column(Float, nullable=False, comment="Tempo de processamento em milissegundos")
    query_count = Column(Integer, nullable=False, comment="Número de queries SQL executadas")
    created_at = Column(DateTime, default=datetime.utcnow, comment="Timestamp do registro")

