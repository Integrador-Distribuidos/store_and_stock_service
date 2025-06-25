from sqlalchemy.orm import Session
from app.models import models
from app.schemas import movement as schemas
from fastapi import HTTPException
from datetime import date

def create_stock_movement(db: Session, movement: schemas.StockMovementCreate):
    '''
    transfer: transfere produto de um estoque para outro (sai de um, entra em outro).

in: entrada de produto no estoque (ex: compra, produção).

out: saída de produto do estoque (ex: venda, perda).

Cada tipo define como a quantidade será ajustada nos estoques.
    '''
    db_movement = models.StockMovement(**movement.model_dump())

    # Verifica se o produto está no estoque de origem
    origin_stock = None
    if db_movement.id_stock_origin:
        origin_stock = (
            db.query(models.ProductStock)
            .filter_by(id_product=db_movement.id_product, id_stock=db_movement.id_stock_origin)
            .first()
        )

    # Verifica se o produto está no estoque de destino
    destination_stock = None
    if db_movement.id_stock_destination:
        destination_stock = (
            db.query(models.ProductStock)
            .filter_by(id_product=db_movement.id_product, id_stock=db_movement.id_stock_destination)
            .first()
        )

    # Ações baseadas no tipo de movimentação
    if db_movement.movement_type == "transfer":
        # Valida origem e destino
        if not origin_stock:
            raise HTTPException(status_code=400, detail="Produto não encontrado no estoque de origem.")
        if origin_stock.quantity < db_movement.quantity:
            raise HTTPException(status_code=400, detail="Estoque de origem insuficiente para transferência.")

        # Debita do estoque origem
        origin_stock.quantity -= db_movement.quantity
        origin_stock.last_update_date = date.today()
        db.flush()

        # Credita no estoque destino
        if destination_stock:
            destination_stock.quantity += db_movement.quantity
            destination_stock.last_update_date = date.today()
        else:
            destination_stock = models.ProductStock(
                id_product=db_movement.id_product,
                id_stock=db_movement.id_stock_destination,
                quantity=db_movement.quantity,
                last_update_date=date.today()
            )
            db.add(destination_stock)
        db.flush()

    elif db_movement.movement_type == "in":
        if not db_movement.id_stock_destination:
            raise HTTPException(status_code=400, detail="Estoque de destino obrigatório para entrada.")

        if destination_stock:
            destination_stock.quantity += db_movement.quantity
            destination_stock.last_update_date = date.today()
        else:
            destination_stock = models.ProductStock(
                id_product=db_movement.id_product,
                id_stock=db_movement.id_stock_destination,
                quantity=db_movement.quantity,
                last_update_date=date.today()
            )
            db.add(destination_stock)
        db.flush()

    elif db_movement.movement_type == "out":
        if not origin_stock:
            raise HTTPException(status_code=400, detail="Produto não encontrado no estoque de origem para saída.")
        if origin_stock.quantity < db_movement.quantity:
            raise HTTPException(status_code=400, detail="Estoque insuficiente para saída.")

        origin_stock.quantity -= db_movement.quantity
        origin_stock.last_update_date = date.today()
        db.flush()

    else:
        raise HTTPException(status_code=400, detail="Tipo de movimentação inválido.")

    # Registra a movimentação
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)

    return db_movement


def get_all_stock_movements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.StockMovement).offset(skip).limit(limit).all()

def get_stock_movement(db: Session, movement_id: int):
    return db.query(models.StockMovement).filter(models.StockMovement.id_movement == movement_id).first()

def get_movements_by_product(db: Session, product_id: int):
    return db.query(models.StockMovement).filter(models.StockMovement.id_product == product_id).all()

def delete_movement():
    pass
