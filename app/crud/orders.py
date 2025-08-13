from app.models import order, order_item, store
from app.models import models
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from app.schemas.order import OrderCreate, OrderOut, OrderItemPatch, OrderStatus
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo

def finalize_order_logic(id: int, db: Session):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    db_order.status = OrderStatus.PAID
    db.commit()

    items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == id).all()
    loja = db.query(store.Store).filter(store.Store.id_store == db_order.id_store).first()
    for item in items:
        product = db.query(models.Product).filter(models.Product.id_product == item.id_product).first()
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        new_balance = loja.balance + Decimal(item.subtotal)
        loja.balance = new_balance
        new_quantity = product.quantity - item.quantity
        product.quantity = new_quantity
        db.commit()

    now_brazil = datetime.now(ZoneInfo("America/Sao_Paulo"))
    new_order = order.Order(
        id_user=db_order.id_user,
        id_store=db_order.id_store,
        status=OrderStatus.DRAFT,
        order_date=now_brazil,
        total_value=0.0,
        creation_date=now_brazil
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order
