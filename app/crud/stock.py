from sys import audit
from sqlalchemy import null
from sqlalchemy.orm import Session
from app.schemas import stock as schemas
from app.models import models
from fastapi import HTTPException
from datetime import date
from app.utils.audit import obtain_data,stock_audit_

# CRUD de Estoque
# -----------------------

def create_stock(db: Session, stock: schemas.StockCreate):
    db_stock = models.Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    new_data = obtain_data(db_stock)
    stock_audit_(
        db=db,
        id_stock=db_stock.id_stock,
        operation="CREATE",
        new_data=new_data,
        old_data={},
        changed_by=1#Trocar pelo id do usuário que alterou
    )
    db.refresh(db_stock)
    return db_stock

def create_ProductStock(db: Session, stock: schemas.StockCreate):
    db_productstock = models.ProductStock(**stock.model_dump())
    stock_exists = db.query(models.Stock).filter(models.Stock.id_stock == db_productstock.id_stock).first()
    product_exists = db.query(models.Product).filter(models.Product.id_product == db_productstock.id_product).first()
    if not stock_exists:
        raise HTTPException(status_code=404, detail="Estoque não encontrado!")
    elif not product_exists:
        raise HTTPException(status_code=404, detail="Produto não encotrado!")
    db.add(db_productstock)
    db.commit()
    db.refresh(db_productstock)
    new_data = obtain_data(db_productstock)
    stock_audit_(
        db=db,
        id_stock=db_productstock.id_stock,
        operation="ADD_PRODUCT_TO_STOCK",
        old_data={},  # como é criação, não há dado anterior
        new_data=new_data,
        changed_by=1  # Substitua pelo ID real do usuário autenticado
    )
    return db_productstock

def get_stock(db: Session, stock_id: int):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encontrado!")

    products = (
        db.query(models.Product.id_product, models.Product.name, models.ProductStock.quantity)
        .join(models.ProductStock, models.ProductStock.id_product == models.Product.id_product)
        .filter(models.ProductStock.id_stock == stock.id_stock)
        .all()
    )
    products_list = [schemas.ProductStockOutInfo(id_product=p.id_product, name=p.name, quantity=p.quantity) for p in products]

    return schemas.StockOut(
        id_stock=stock.id_stock,
        name=stock.name,
        city=stock.city,
        uf=stock.uf,
        zip_code=stock.zip_code,
        address=stock.address,
        creation_date=stock.creation_date,
        products=products_list,
    )


def get_all_stocks(db: Session, skip: int = 0, limit: int = 100):
    stocks = db.query(models.Stock).offset(skip).limit(limit).all()
    results = []

    for stock in stocks:
        products = (
            db.query(models.Product.id_product, models.Product.name, models.ProductStock.quantity)
            .join(models.ProductStock, models.ProductStock.id_product == models.Product.id_product)
            .filter(models.ProductStock.id_stock == stock.id_stock)
            .all()
        )
        products_list = [schemas.ProductStockOutInfo(id_product=p.id_product, name=p.name, quantity=p.quantity) for p in products]

        results.append(
            schemas.StockOut(
                id_stock=stock.id_stock,
                name=stock.name,
                city=stock.city,
                uf=stock.uf,
                zip_code=stock.zip_code,
                address=stock.address,
                creation_date=stock.creation_date,
                products=products_list,
            )
        )
    if not results:
        raise HTTPException(status_code=404, detail="Nenhum estoque encontrado!")

    return results



def delete_stock(db: Session, stock_id: int):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if stock:
        old_data = obtain_data(stock)
        stock_audit_(
            db=db,
            id_stock=stock.id_stock,
            operation="DELETE",
            old_data=old_data,
            new_data={},
            changed_by=1#Trocar pelo id do usuário que alterou
        )
        db.query(models.ProductStock).filter(models.ProductStock.id_stock == stock_id).delete()
        db.delete(stock)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encontrado!")
    return stock


def update_stock(db: Session, stock_id: int, stock_data: schemas.StockCreate):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if stock:
        old_data = obtain_data(stock)
        for field, value in stock_data.model_dump().items():
            setattr(stock, field, value)
        db.commit()
        new_data = obtain_data(stock)
        stock_audit_(
            db=db,
            id_stock=stock.id_stock,
            operation="UPDATE",
            new_data=new_data,
            old_data=old_data,
            changed_by=1#Trocar pelo id do usuário que alterou
        )
        db.refresh(stock)
    else: 
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encotrado!")
    return stock
