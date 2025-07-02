from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class OrderAuditBase(BaseModel):
    id_order: int
    operation: str
    old_data: Optional[dict]
    new_data: Optional[dict]
    changed_by: int
    date: datetime

class OrderAuditOut(OrderAuditBase):
    id_order_audit: int

    class Config:
        from_attribute = True
