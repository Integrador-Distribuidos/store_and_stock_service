from app.dependencies.auth import get_current_user
from app.schemas import product as schemas
from sqlalchemy.orm import Session
from app.crud import product as crud
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.database import get_db
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import date
from app.utils.file_utils import save_upload_file, validate_file, UPLOAD_FOLDER

router = APIRouter(prefix="/api")

# ------------------------
# ROTAS DE PRODUTOS
# ------------------------


#Cadastrar produto
@router.post("/products/", response_model=schemas.ProductOut)
def create_product(
        db: Session = Depends(get_db),
        user_data: dict = Depends(get_current_user),
        id_stock: int = Form(...),
        name: str = Form(...),
        description: str = Form(...),
        price: float = Form(...),
        sku: str = Form(...),
        category: str = Form(...),
        quantity: Optional[int] = Form(1),
        creation_date: date = Form(...),
        image: Optional[UploadFile] = File(None),
    ):
    return crud.create_product(
        db=db, 
        id_stock=id_stock,
        user_data=user_data, 
        name=name, image=image, 
        description=description, 
        price=price, sku=sku, 
        category=category, 
        quantity=quantity, 
        creation_date=creation_date)    


#Consultar todos os produtos
@router.get("/products/all", response_model=list[schemas.ProductOut])
def read_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)): 
    return crud.get_all_products_with_stock(db, skip, limit)


#Consultar produtos com base no user id
@router.get("/products/", response_model=list[schemas.ProductOut])
def read_products_with_user_id(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)): 
    return crud.get_products_with_userid(db=db, skip=skip, limit=limit, user_data=user_data)

#Consultar produto específico
@router.get("/products/{id}", response_model=schemas.ProductOut)
def read_product(id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")
    return product


#Alterar produto
@router.put("/products/{id}", response_model=schemas.ProductOut)
def update_product(
    id: int,
    db: Session = Depends(get_db),
    id_stock: Optional[int] = Form(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    sku: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    quantity: Optional[int] = Form(None),
    creation_date: Optional[date] = Form(None),
    image: Optional[UploadFile] = File(None),
    user_data: dict = Depends(get_current_user)
):
    updated_product = crud.update_product(
        db=db,
        product_id=id,
        id_stock=id_stock,
        name=name,
        description=description,
        price=price,
        sku=sku,
        category=category,
        quantity=quantity,
        creation_date=creation_date,
        user_data=user_data,
        image=image
    )

    return updated_product



#Deletar produto
@router.delete("/products/{id}", response_model=schemas.ProductOut)
def delete_product(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    product = crud.delete_product(db, id, user_data=user_data)
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Produto não Encontrado!"})
    return JSONResponse(content={"detail": "Produto Deletado!"})