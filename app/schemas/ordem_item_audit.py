from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OrderItemAuditOut(BaseModel):
    id_order_item_audit: int
    id_order_item: int
    operation: str
    old_data: Optional[dict]
    new_data: Optional[dict]
    changed_by: int
    date: datetime

    class Config:
        from_attributes = True
