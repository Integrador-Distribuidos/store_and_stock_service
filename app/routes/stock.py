from app.dependencies.auth import get_current_user
from app.schemas import stock as schemas
from app.schemas import product
from app.crud import stock as crud
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Header
from app.models import stock_audit
from app import database

router = APIRouter(prefix="/api")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROTAS DE ESTOQUE

#Cadastrar estoque
@router.post("/stocks/", response_model=schemas.StockOut)
def create_stock(stock: schemas.StockCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    return crud.create_stock(db, stock, user_data=user_data)

#Cadastrar produto no estoque
@router.post("/stocks/product", response_model=product.ProductStockOut)
def create_productstock(stock: product.ProductStock, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    return crud.create_ProductStock(db, stock, user_data=user_data)

#Consultar estoque específico
@router.get("/stocks/{id}", response_model=schemas.StockOut)
def read_stock(id: int, db: Session = Depends(get_db)):
    stock = crud.get_stock(db, id)
    if not stock:
        raise HTTPException(status_code=404, detail="Estoque não encontrado!")
    return stock


#Consultar todos os estoques
@router.get("/stocks/all", response_model=list[schemas.StockOut])
def read_all_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_stocks(db, skip, limit)


#Consultar estoques por usuário com base no token fornecido
@router.get("/stocks/", response_model=list[schemas.StockOut])
def read_stocks_for_userid(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    return crud.get_stocks_for_user(db=db, skip=skip, limit=limit, user_data=user_data)

#Alterar estoque
@router.put("/stocks/{id}", response_model=schemas.StockOut)
def update_stock(id: int, stock: schemas.StockCreate, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    return crud.update_stock(db, id, stock, user_data=user_data)


#Deletar estoque
@router.delete("/stocks/{id}", response_model=schemas.StockOut)
def delete_stock(id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    return crud.delete_stock(db, id, user_data=user_data)