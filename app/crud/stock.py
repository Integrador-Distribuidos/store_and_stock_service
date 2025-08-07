from sqlalchemy.orm import Session
from app.schemas import stock as schemas
from app.models import models
from fastapi import HTTPException

# CRUD de Estoque
# -----------------------

def create_stock(db: Session, stock: schemas.StockCreate, user_data: dict):
    db_stock = models.Stock(**stock.model_dump())
    db_stock.created_by = int(user_data.get('user_id'))
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock
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
    return db_productstock

def get_stock(db: Session, stock_id: int):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encontrado!")

    # Acessa diretamente a relação entre estoque e produtos
    products_list = [
        schemas.ProductStockOutInfo(
            id_product=p.id_product,
            name=p.name,
            quantity=p.quantity,
            price=p.price,
            image=p.image
        )
        for p in stock.products  # relação direta
    ]

    return schemas.StockOut(
        id_stock=stock.id_stock,
        id_store=stock.id_store,
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
        # Acessa os produtos relacionados diretamente via relacionamento 'products'
        products_list = [
            schemas.ProductStockOutInfo(
                id_product=p.id_product,
                name=p.name,
                quantity=p.quantity,
                price=p.price,
                image=p.image
            )
            for p in stock.products  # aqui acessa diretamente os produtos do estoque
        ]

        results.append(
            schemas.StockOut(
                id_stock=stock.id_stock,
                id_store=stock.id_store,
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

def get_stocks_for_user(db: Session, user_data: dict, skip: int = 0, limit: int = 100):
    user_id = int(user_data.get("user_id"))
    
    stocks = (
        db.query(models.Stock)
        .filter(models.Stock.created_by == user_id)  # filtro pelo usuário
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    results = []
    for stock in stocks:
    # Consulta os produtos pertencentes a um estoque específico
        products = (
            db.query(
                models.Product.id_product,
                models.Product.name,
                models.Product.quantity,
                models.Product.image,
                models.Product.price
            )
            .filter(models.Product.id_stock == stock.id_stock)  # Join não é necessário
            .all()
        )

        # Transforma os produtos encontrados em uma lista de schemas de saída
        products_list = [
            schemas.ProductStockOutInfo(
                id_product=p.id_product,
                name=p.name,
                quantity=p.quantity,
                price=p.price,
                image=p.image
            )
            for p in products
        ]

        # Adiciona o estoque com os produtos ao resultado final
        results.append(
            schemas.StockOut(
                id_stock=stock.id_stock,
                id_store=stock.id_store,
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

def delete_stock(db: Session, stock_id: int, user_data: dict):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encontrado!")

    products_to_delete = db.query(models.Product).filter(models.Product.id_stock == stock_id).all()
    product_ids = [p.id_product for p in products_to_delete]

    if product_ids:
        # Deletar movimentações dos produtos
        db.query(models.StockMovement).filter(models.StockMovement.id_product.in_(product_ids)).delete(synchronize_session=False)

        # Deletar os produtos
        db.query(models.Product).filter(models.Product.id_product.in_(product_ids)).delete(synchronize_session=False)

    # Deletar o estoque
    db.delete(stock)
    db.commit()

    return stock


def update_stock(db: Session, stock_id: int, stock_data: schemas.StockCreate, user_data: dict):
    stock = db.query(models.Stock).filter(models.Stock.id_stock == stock_id).first()
    if stock:
        for field, value in stock_data.model_dump().items():
            setattr(stock, field, value)
        db.commit()
        db.refresh(stock)
    else: 
        raise HTTPException(status_code=404, detail=f"Estoque com ID {stock_id} não encotrado!")
    return stock
