from fastapi import FastAPI, Depends, HTTPException, Path, status, APIRouter, UploadFile, File, Query
from app.database import Base, engine
from app.models import store, order, order_item
from app.schemas.store import StoreCreate, StoreOut
from app.database import get_db
from app.utils.file_utils import save_upload_file, validate_file, UPLOAD_FOLDER
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


@router.get("/api/stores/", response_model=List[StoreOut])
def list_stores(city: str = Query(None), uf: str = Query(None),db: Session = Depends(get_db)):
    query = db.query(store.Store)

    if city:
        query = query.filter(store.Store.city.ilike(f"%{city}%"))
    if uf:
        query = query.filter(store.Store.uf.ilike(f"%{uf}%"))

    return query.all()

@router.get("/api/stores/{id}/", response_model=StoreOut)
def get_store(id: int = Path(..., description="ID loja"), db:Session = Depends(get_db)):
    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return store_obj

@router.post("/api/stores/", response_model=StoreOut)
def create_store(store_data: StoreCreate, db: Session = Depends(get_db)):
    existing_store = db.query(store.Store).filter(
        (store.Store.cnpj == store_data.cnpj) | 
        (store.Store.email == store_data.email)
    ).first()
    if existing_store:
        raise HTTPException(status_code=400, detail="CNPJ ou email já cadastrado.")

    new_store = store.Store(**store_data.dict())
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store

@router.put("/api/stores/{id}/", response_model=StoreOut)
def update_store(id: int, store_data: StoreCreate, db: Session = Depends(get_db)):
    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    conflict = db.query(store.Store).filter(
        ((store.Store.cnpj == store_data.cnpj) | (store.Store.email == store_data.email)) &
        (store.Store.id_store != id)
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="CNPJ ou email já cadastrado em outra loja.")

    for key, value in store_data.dict().items():
        setattr(store_obj, key, value)

    db.commit()
    db.refresh(store_obj)
    return store_obj

@router.delete("/api/stores/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(id: int, db: Session = Depends(get_db)):
    store_obj = db.query(store.Store).filter(store.Store.id_store == id).first()
    if not store_obj:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    has_orders = db.query(order.Order).filter(order.Order.id_store == id).first()
    if has_orders:
        raise HTTPException(
            status_code=400,
            detail="Não é possível deletar a loja pois existem pedidos associados a ela."
        )

    db.delete(store_obj)
    db.commit()
    return

@router.post("/api/stores/{store_id}/upload-image/")
def upload_store_image(store_id: int, db: Session = Depends(get_db), file: UploadFile = File(...)):
    stores = db.query(store.Store).filter(store.Store.id_store == store_id).first()
    if not stores:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    
    old_image = stores.image or ""

    ext = validate_file(file)
    filename = f"store_{store_id}.{ext}"
    filepath = save_upload_file(upload_file=file, folder=UPLOAD_FOLDER, filename=filename, old_image=old_image)

    stores.image = filename

    db.commit()

    return {"message": "Imagem enviada com sucesso", "filename": filename}
