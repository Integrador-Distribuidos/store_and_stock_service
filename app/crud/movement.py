from sqlalchemy.orm import Session
from app.models import models
from app.schemas import movement as schemas
from fastapi import HTTPException
from datetime import date

def create_stock_movement(db: Session, movement: schemas.StockMovementCreate, user_data: dict):
    user_id = int(user_data.get("user_id"))
    '''
    Transfere produto de um estoque para outro (sai de um, entra em outro).
    '''

    if movement.id_stock_origin == movement.id_stock_destination:
        raise HTTPException(status_code=406, detail="Estoque de origem e destino são iguais.")

    # Busca produto no estoque de origem
    origin_product = db.query(models.Product).filter_by(
        id_product=movement.id_product,
        id_stock=movement.id_stock_origin
    ).first()

    if not origin_product:
        raise HTTPException(status_code=400, detail="Produto não encontrado no estoque de origem.")

    if origin_product.quantity < movement.quantity:
        raise HTTPException(status_code=400, detail="Estoque de origem insuficiente para transferência.")

    # Busca produto equivalente no estoque de destino (mesmo SKU)
    destination_product = db.query(models.Product).filter_by(
        sku=origin_product.sku,
        id_stock=movement.id_stock_destination
    ).first()

    # Atualiza estoque origem
    origin_product.quantity -= movement.quantity
    origin_product.last_update_date = date.today()

    # Atualiza ou cria produto no destino
    if destination_product:
        destination_product.quantity += movement.quantity
        destination_product.last_update_date = date.today()
    else:
        destination_product = models.Product(
            name=origin_product.name,
            sku=origin_product.sku,
            description=origin_product.description,
            price=origin_product.price,
            image=origin_product.image,
            category=origin_product.category,
            quantity=movement.quantity,
            id_stock=movement.id_stock_destination,
            creation_date=date.today()
        )
        db.add(destination_product)

    # Registra movimentação
    db_movement = models.StockMovement(**movement.model_dump())
    db_movement.created_by = user_id
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