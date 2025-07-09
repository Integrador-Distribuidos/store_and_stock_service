from sqlalchemy.orm import Session
from app.models import models
from app.schemas import product as schemas
from fastapi import HTTPException
from datetime import date
# -----------------------
# CRUD de Produto
# -----------------------

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_all_products_with_stock(db: Session, skip: int = 0, limit: int = 100):
    products = (
        db.query(models.Product)
        .offset(skip)
        .limit(limit)
        .all()
    )

    product_ids = [p.id_product for p in products]

    stocks = (
        db.query(models.ProductStock)
        .filter(models.ProductStock.id_product.in_(product_ids))
        .all()
    )

    stock_map = {}
    for stock in stocks:
        if stock.id_stock is not None:  # filtra estoques inválidos
            stock_map.setdefault(stock.id_product, []).append({
                "id_stock": stock.id_stock,
                "quantity": stock.quantity
            })

    return [
        {
            "id_product": p.id_product,
            "name": p.name,
            "image": p.image,
            "description": p.description,
            "price": p.price,
            "sku": p.sku,
            "category": p.category,
            "creation_date": p.creation_date,
            "stocks": stock_map.get(p.id_product, [])
        }
        for p in products
    ]



def get_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")

    stock_entries = (
        db.query(models.ProductStock.id_stock, models.ProductStock.quantity)
        .filter(models.ProductStock.id_product == product_id)
        .all()
    )

    return {
        "id_product": product.id_product,
        "name": product.name,
        "image": product.image,
        "description": product.description,
        "price": product.price,
        "sku": product.sku,
        "category": product.category,
        "creation_date": product.creation_date,
        "stocks": [
            {"id_stock": s.id_stock, "quantity": s.quantity}
            for s in stock_entries
        ]
    }


def update_product(db: Session, product_id: int, product_data: schemas.ProductUpdate):
    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")

    # Atualiza só os campos que vieram no JSON (diferentes de None)
    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(product, field):
            setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product



def delete_product(db: Session, product_id: int):
    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")
        # Apagar registros relacionados em product_stock
    db.query(models.ProductStock).filter(models.ProductStock.id_product == product_id).delete()
    db.query(models.StockMovement).filter(models.StockMovement.id_product == product_id).delete()
    try:
        db.delete(product)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not delete product: {str(e)}")
    return {"detail": "Produto  deletado"}

