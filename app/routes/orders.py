
from fastapi import Depends, HTTPException, Path, status, APIRouter
from app.models import store, order, order_item
from app.schemas.order import OrderCreate, OrderOut
from app.crud.product import get_product
from app.schemas.order_item import OrderItemCreate, OrderItemOut
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.post("/api/orders/", response_model=OrderOut)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    store_exists = db.query(store.Store).filter(store.Store.id_store == order_data.id_store).first()
    if not store_exists:
        raise HTTPException(status_code=400, detail="Loja informada não existe.")

    new_order = order.Order(**order_data.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/api/orders/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(order.Order).all()
    return orders

@router.get("/api/orders/{id}/", response_model=OrderOut)
def get_order(id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_order

@router.put("/api/orders/{id}/", response_model=OrderOut)
def update_order(id: int, order_data: OrderCreate, db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    for field, value in order_data.dict().items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/api/orders/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: int, db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    has_items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == id).first()
    if has_items:
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar o pedido pois existem itens associados a ele."
        )

    db.delete(db_order)
    db.commit()
    return

@router.get("/api/orders/{id}/items/", response_model=List[OrderItemOut])
def list_order_items(id: int, db: Session = Depends(get_db)):
    items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == id).all()
    return items

@router.post("/api/orders/{id}/items/", response_model=OrderItemOut)
def create_order_item(id: int, item_data: OrderItemCreate, db: Session = Depends(get_db)):
    new_item = order_item.OrderItem(**item_data.dict(), id_order=id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@router.put("/api/orders/items/{id}/", response_model=OrderItemOut)
def update_order_item(id: int, item_data: OrderItemCreate, db: Session = Depends(get_db)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    for field, value in item_data.dict().items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

@router.delete("/api/orders/items/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(id: int, db: Session = Depends(get_db)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    db.delete(item)
    db.commit()
    return {"detail": "Item do pedido deletado com sucesso"}