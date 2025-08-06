from sqlalchemy.orm import Session
from app.models import models
from app.utils.file_utils import save_upload_file, validate_file, UPLOAD_FOLDER
from app.schemas import product as schemas
from fastapi import HTTPException, UploadFile
# -----------------------
# CRUD de Produto
# -----------------------

def create_product(db: Session, product: schemas.ProductCreate, user_data: dict):
    user_id = int(user_data.get('user_id'))
    db_product = models.Product(**product.model_dump())
    stock_exists = db.query(models.Stock).filter(models.Stock.id_stock == db_product.id_stock).first()
    if not stock_exists:
        raise HTTPException(status_code=404, detail="Estoque não encontrado!")
    db_product.created_by = user_id
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products_with_userid(db: Session, user_data: dict, skip: int = 0, limit: int = 100):
    user_id = int(user_data.get("user_id"))
    
    products = (
        db.query(models.Product)
        .filter(models.Product.created_by == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    if not products:
        raise HTTPException(status_code=404, detail="Nenhum produto encontrado!")

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
                    "id_stock": p.id_stock,
                    "quantity": p.quantity
                }
            ] if p.id_stock is not None else []
        }
        for p in products
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

def update_product(db: Session, product_id: int, product_data: schemas.ProductUpdate, user_data: dict):
    user_id = int(user_data.get('user_id'))
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
