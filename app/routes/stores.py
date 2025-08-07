from datetime import date
from email.mime import image
import os
from fastapi import FastAPI, Depends, Form, HTTPException, Path, status, APIRouter, UploadFile, File, Query
from app.database import Base, engine
from app.dependencies.auth import get_current_user
from app.models import store, order, order_item
from app.schemas.store import StoreCreate, StoreOut
from app.database import get_db
from app.utils.file_utils import save_upload_file, validate_file, UPLOAD_FOLDER
from sqlalchemy.orm import Session
from typing import List
from app.models.models import Product, Stock
from typing import Optional

router = APIRouter()


@router.get("/api/stores/all", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(store.Store).all()
    return stores

@router.get("/api/stores/", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    user_id = int(user_data.get("user_id"))
    stores = db.query(store.Store).filter(store.Store.created_by == user_id).all()
    return stores

@router.get("/api/stores/{id}/", response_model=StoreOut)
def get_store(id: int = Path(..., description="ID loja"), db:Session = Depends(get_db)):
    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return store_obj

@router.post("/api/stores/", response_model=StoreOut)
def create_store(
    name: str = Form(...),
    email: str = Form(...),
    cnpj: str = Form(...),
    creation_date: date = Form(...),
    phone_number: str = Form(...),
    db: Session = Depends(get_db), 
    user_data: dict = Depends(get_current_user),
    image: Optional[UploadFile] = File(None)
):
    existing_store = db.query(store.Store).filter(
        (store.Store.cnpj == cnpj) | 
        (store.Store.email == email)
    ).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="CNPJ ou email já cadastrado.")

    new_store = store.Store( 
        name=name, 
        email=email, 
        cnpj=cnpj, 
        creation_date=creation_date, 
        phone_number=phone_number
    )
    new_store.created_by = int(user_data.get('user_id'))
    
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    if image:
        ext = validate_file(image)
        filename = f"store_{new_store.id_store}.{ext}"
        save_upload_file(upload_file=image, folder=UPLOAD_FOLDER, filename=filename, old_image="")
        new_store.image = filename
        db.commit()
    return new_store

@router.put("/api/stores/{id}/", response_model=StoreOut)
def update_store(
    id: int,
    name: str = Form(...),
    cnpj: str = Form(...),
    creation_date: str = Form(...),  # você pode converter para date depois
    email: str = Form(...),
    phone_number: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_data: dict = Depends(get_current_user)
):

    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    conflict = db.query(store.Store).filter(
        ((store.Store.cnpj == cnpj) | (store.Store.email == email)) &
        (store.Store.id_store != id)
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="CNPJ ou email já cadastrado em outra loja.")

    # Atualiza os campos de texto
    store_obj.name = name
    store_obj.cnpj = cnpj
    store_obj.creation_date = creation_date
    store_obj.email = email
    store_obj.phone_number = phone_number

    # Se uma imagem foi enviada, salva e atualiza
    if image:
        ext = validate_file(image)
        filename = f"store_{id}.{ext}"
        print(f"Salvando imagem: {filename}")
        save_upload_file(upload_file=image, folder=UPLOAD_FOLDER, filename=filename, old_image=store_obj.image)
        store_obj.image = filename

    db.commit()
    db.refresh(store_obj)
    return store_obj

@router.delete("/api/stores/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    has_orders = db.query(order.Order).filter(order.Order.id_store == id).first()
    if has_orders:
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar a loja pois existem pedidos associados a ela."
        )
    

    # Busca estoques associados à loja
    stocks = db.query(Stock).filter(Stock.id_store == id).all()

    for stk in stocks:
        # Deleta produtos diretamente associados a este estoque
        db.query(Product).filter(Product.id_stock == stk.id_stock).delete()

        # Deleta o estoque
        db.delete(stk)

    if store_obj.image:
        caminho_imagem = os.path.join(UPLOAD_FOLDER, store_obj.image)
        if os.path.exists(caminho_imagem):
            os.remove(caminho_imagem)

    # Deleta a loja
    db.delete(store_obj)
    db.commit()
    return {"message": "Loja deletada com sucesso!"}
