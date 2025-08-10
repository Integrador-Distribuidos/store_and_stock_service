
from sqlalchemy.orm import Session, joinedload
from app.models import models
from app.utils.file_utils import save_upload_file, validate_file, UPLOAD_FOLDER
from app.schemas import product as schemas
from fastapi import HTTPException, UploadFile, File, Form
from typing import Optional
from datetime import date
# -----------------------
# CRUD de Produto
# -----------------------
def create_product(
        db: Session, 
        user_data: dict,
        name: str,
        description: str,
        price: float,
        sku: str,
        category: str,
        creation_date: date,
        id_stock: int,
        image: Optional[UploadFile] = File(None),
        quantity: Optional[int] = Form(1),
    ):
    user_id = int(user_data.get('user_id'))
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        sku=sku,
        category=category,
        quantity=quantity,
        creation_date=creation_date,
        id_stock=id_stock,
        created_by=user_id
    )
    stock_exists = db.query(models.Stock).filter(models.Stock.id_stock == db_product.id_stock).first()
    if not stock_exists:
        raise HTTPException(status_code=404, detail="Estoque não encontrado!")
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    if image:
        ext = validate_file(image)
        filename = f"product_{db_product.id_product}.{ext}"
        filepath = save_upload_file(upload_file=image, folder=UPLOAD_FOLDER, filename=filename, old_image=db_product.image or "")
        db_product.image = filename
        db.commit()
    return db_product


def get_products_with_userid(db: Session, user_data: dict, skip: int = 0, limit: int = 100):
    user_id = int(user_data.get("user_id"))

    # INNER JOIN manual
    results = (
        db.query(models.Product, models.Stock)
        .join(models.Stock, models.Product.id_stock == models.Stock.id_stock)
        .filter(models.Product.created_by == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado!")
    
    print("Resultados do JOIN:", results)  # Debugging line
    for p, s in results:
        print(f"Produto: {p.name}, Estoque: {s.name}")

    # Correção: preenche todos os campos de estoque vindos do join
    return [
        {
            "id_product": p.id_product,
            "id_stock": p.id_stock,
            "name": p.name,
            "image": p.image,
            "description": p.description,
            "price": p.price,
            "sku": p.sku,
            "category": p.category,
            "quantity": p.quantity,
            "creation_date": p.creation_date,
            "stocks": [
                {
                    "id_stock": s.id_stock,
                    "quantity": p.quantity,
                    "name": s.name,
                    "city": s.city,
                    "uf": s.uf,
                    "zip_code": s.zip_code,
                    "address": s.address,
                    "creation_date": s.creation_date,
                }
            ]
        }
        for p, s in results
    ]

def get_all_products_with_stock(db: Session, skip: int = 0, limit: int = 100):
    products = (
        db.query(models.Product)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "id_product": p.id_product,
            "id_stock": p.id_stock,
            "name": p.name,
            "image": p.image,
            "description": p.description,
            "price": p.price,
            "sku": p.sku,
            "category": p.category,
            "quantity": p.quantity,
            "creation_date": p.creation_date,
            "stock": {
                "id_stock": p.stock.id_stock,
                "name": p.stock.name,
                "city": p.stock.city,
                "uf": p.stock.uf,
                "zip_code": p.stock.zip_code,
                "address": p.stock.address,
                "creation_date": p.stock.creation_date,
            } if p.stock else None
        }
        for p in products
    ]

def get_product(db: Session, product_id: int):
    product = (
        db.query(models.Product)
        .filter(models.Product.id_product == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")

    return {
        "id_product": product.id_product,
        "id_stock": product.id_stock,
        "name": product.name,
        "image": product.image,
        "description": product.description,
        "price": product.price,
        "sku": product.sku,
        "category": product.category,
        "quantity": product.quantity,
        "creation_date": product.creation_date,
        "stock": {
            "id_stock": product.stock.id_stock,
            "name": product.stock.name,
            "city": product.stock.city,
            "uf": product.stock.uf,
            "zip_code": product.stock.zip_code,
            "address": product.stock.address,
        } if product.stock else None
    }

def update_product(
        db: Session, 
        product_id: int,
        user_data: dict,
        id_stock: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        sku: Optional[str] = None,
        category: Optional[str] = None,
        quantity: Optional[int] = None,
        creation_date: Optional[date] = None,
        image: Optional[UploadFile] = None
        ):
    



    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")

    # Atualiza só se o valor existir (não None)
    if id_stock is not None:
        stock = db.query(models.Stock).filter(models.Stock.id_stock == id_stock).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Estoque não encontrado para o produto.")
        product.id_stock = id_stock

    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if sku is not None:
        product.sku = sku
    if category is not None:
        product.category = category
    if quantity is not None:
        product.quantity = quantity
    if creation_date is not None:
        product.creation_date = creation_date

    # Atualiza imagem
    if image:
        ext = validate_file(image)
        filename = f"product_{product_id}.{ext}"
        filepath = save_upload_file(upload_file=image, folder=UPLOAD_FOLDER, filename=filename, old_image=product.image)
        product.image = filename

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int, user_data: dict):
    user_id = int(user_data.get('user_id'))
    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Produto com ID {product_id} não encontrado")
        # Apagar registros relacionados em product_stock
        # Captura o estado anterior (deepcopy é opcional, mas evita mutações futuras)

    db.query(models.StockMovement).filter(models.StockMovement.id_product == product_id).delete()
    try:
        db.delete(product)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not delete product: {str(e)}")
    return {"detail": "Produto  deletado"}




def upload_product_image(product_id: int, db: Session, file: UploadFile):
    product = db.query(models.Product).filter(models.Product.id_product == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    old_image = product.image or ""
    ext = validate_file(file)
    filename = f"product_{product_id}.{ext}"
    filepath = save_upload_file(upload_file=file, folder=UPLOAD_FOLDER,filename=filename, old_image=old_image)
    product.image = filename
    db.commit()
    return {"message": "Imagem enviada com sucesso", "filename": filename}
