from fastapi import Depends, HTTPException, Path, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from app.crud import orders
from app.models import store, order, order_item
from app.schemas.order import OrderCreate, OrderOut, OrderItemPatch, OrderStatus
from app.crud.product import get_product
from app.dependencies.auth import get_current_user
from app.schemas.order_item import OrderItemCreate, OrderItemOut
from app.database import get_db
from app.models import models
from datetime import datetime
from zoneinfo import ZoneInfo

from app.strategies.order_total_value import OrderTotalCalculationStrategy, RegularOrderTotalCalculation, DiscountedOrderTotalCalculation

router = APIRouter()

def recalculate_order_total(order_id: int, db: Session, strategy: OrderTotalCalculationStrategy):
    total_value = strategy.calculate_total(db, order_id)
    db_order = db.query(order.Order).filter(order.Order.id_order == order_id).first()
    db_order.total_value = total_value
    db.commit()

@router.get("/api/orders/my/", response_model=List[OrderOut])
def list_my_orders(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    user_id = user_data["id_user"]
    orders = db.query(order.Order).filter(order.Order.id_user == user_id).all()
    return orders

@router.get("/api/orders/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(order.Order).all()

@router.post("/api/orders/", response_model=OrderOut)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    now_brazil = datetime.now(ZoneInfo("America/Sao_Paulo"))

    new_order = order.Order(
        **order_data.dict(exclude={"order_date", "creation_date"}),
        order_date=now_brazil,
        creation_date=now_brazil
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.patch("/api/orders/{id}/finalize/", response_model=OrderOut)
def finalize_order(id: int, db: Session = Depends(get_db)):
    return orders.finalize_order_logic(id, db)

@router.get("/api/orders/{id}/", response_model=OrderOut)
def get_order(id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_order

@router.put("/api/orders/{id}/", response_model=OrderOut)
def update_order(id: int, order_data: OrderCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    for field, value in order_data.dict().items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order

@router.patch("/api/orders/{id}/", response_model=OrderOut)
def update_order_status(id: int, status: OrderStatus, db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/api/orders/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if db_order.status != "draft":
        raise HTTPException(status_code=400, detail="Não é possível deletar pedidos finalizados.")

    has_items = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == id).first()
    if has_items:
        raise HTTPException(status_code=400, detail="Não é possível deletar o pedido pois existem itens associados a ele.")

    db.delete(db_order)
    db.commit()
    return

@router.post("/api/orders/{id}/items/", response_model=OrderItemOut)
def create_order_item(id: int, item_data: OrderItemCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id_product == item_data.id_product).first()
    if not product:
        raise HTTPException(status_code=400, detail="Produto não encontrado.")

    existing_item = db.query(order_item.OrderItem).filter(
        order_item.OrderItem.id_order == id,
        order_item.OrderItem.id_product == item_data.id_product
    ).first()

    requested_quantity = item_data.quantity
    existing_quantity = existing_item.quantity if existing_item else 0

    if requested_quantity + existing_quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Quantidade total no carrinho excede o estoque disponível.")

    try:
        if existing_item:
            existing_item.quantity += item_data.quantity
            existing_item.subtotal = existing_item.unit_price * existing_item.quantity
            db.commit()
            db.refresh(existing_item)
        else:
            new_item = order_item.OrderItem(**item_data.dict(), id_order=id)
            db.add(new_item)
            db.commit()
            db.refresh(new_item)

        #strategy = DiscountedOrderTotalCalculation()
        strategy = RegularOrderTotalCalculation()
        recalculate_order_total(id, db, strategy)

        return new_item if not existing_item else existing_item
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erro ao adicionar item ao pedido: {str(e)}")


@router.get("/api/orders/", response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(order.Order).all()

@router.get("/api/orders/{id}/", response_model=OrderOut)
def get_order(id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return db_order

@router.put("/api/orders/{id}/", response_model=OrderOut)
def update_order(id: int, order_data: OrderCreate, db: Session = Depends(get_db),  user_data: dict = Depends(get_current_user)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    for field, value in order_data.dict().items():
        setattr(db_order, field, value)

    db.commit()
    db.refresh(db_order)
    return db_order

@router.delete("/api/orders/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(id: int, db: Session = Depends(get_db),  user_data: dict = Depends(get_current_user)):
    db_order = db.query(order.Order).filter(order.Order.id_order == id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if db_order.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar pedidos finalizados."
        )

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
    return db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order == id).all()

@router.put("/api/orders/items/{id}/", response_model=OrderItemOut)
def update_order_item(id: int, item_data: OrderItemCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    for field, value in item_data.dict().items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)

    #strategy = DiscountedOrderTotalCalculation()
    strategy = RegularOrderTotalCalculation()
    recalculate_order_total(item.id_order, db, strategy)
    return item

@router.delete("/api/orders/items/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    order_id = item.id_order
    db.delete(item)
    db.commit()

    #strategy = DiscountedOrderTotalCalculation()
    strategy = RegularOrderTotalCalculation()
    recalculate_order_total(order_id, db, strategy)
    return {"detail": "Item do pedido deletado com sucesso"}

@router.patch("/api/orders/items/{id}/", response_model=OrderItemOut)
def patch_order_item(id: int, item_data: OrderItemPatch, db: Session = Depends(get_db)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    product = db.query(models.Product).filter(models.Product.id_product == item.id_product).first()
    if not product:
        raise HTTPException(status_code=400, detail="Produto não encontrado.")

    if item_data.quantity and item_data.quantity > product.quantity:
        raise HTTPException(status_code=400, detail="Quantidade solicitada excede o estoque disponível.")

    data = item_data.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)

    if 'quantity' in data:
        item.subtotal = item.unit_price * item.quantity

    db.commit()
    db.refresh(item)

    #strategy = DiscountedOrderTotalCalculation()
    strategy = RegularOrderTotalCalculation()
    recalculate_order_total(item.id_order, db, strategy)
    return item

@router.delete("/api/orders/items/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    item = db.query(order_item.OrderItem).filter(order_item.OrderItem.id_order_item == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item do pedido não encontrado")

    order_id = item.id_order
    db.delete(item)
    db.commit()

    #strategy = DiscountedOrderTotalCalculation()
    strategy = RegularOrderTotalCalculation()
    recalculate_order_total(order_id, db, strategy)
    return {"detail": "Item do pedido deletado com sucesso"}


@router.post("/api/orders/", response_model=OrderOut)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    new_order = order.Order(**order_data.dict())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/api/orders/my", response_model=List[OrderOut])
def list_user_orders(
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = user_data.get('user_id')
    if not user_id:
        raise HTTPException(status_code=401, detail="Usuário não autenticado")
    
    orders = db.query(order.Order).filter(
        order.Order.id_user == user_id,
        order.Order.status == "paid"
    ).all()
    return orders
