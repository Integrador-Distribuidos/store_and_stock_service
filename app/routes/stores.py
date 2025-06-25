from fastapi import FastAPI, Depends, HTTPException, Path, status, APIRouter

from app.database import Base, engine
from app.models import store, order, order_item
from app.schemas.store import StoreCreate, StoreOut
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


@router.get("/api/stores/", response_model=List[StoreOut])
def list_stores(db: Session = Depends(get_db)):
    stores = db.query(store.Store).all()
    return stores

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
