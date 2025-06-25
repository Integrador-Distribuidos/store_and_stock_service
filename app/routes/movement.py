
from app.crud import movement as crud
from sqlalchemy.orm import Session
from app.schemas import movement as schemas
from fastapi import APIRouter, Depends, HTTPException
from app import database
router = APIRouter(prefix="/api")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# ROTAS DE MOVIMENTAÇÃO DE ESTOQUE
# ------------------------
#Criar movimentação
@router.post("/stocks/movements/", response_model=schemas.StockMovementOut)
def create_movement(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    return crud.create_stock_movement(db, movement)

#Consultar Movimentações
@router.get("/stocks/movements/", response_model=list[schemas.StockMovementOut])
def read_all_movements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movements = crud.get_all_stock_movements(db, skip, limit)
    if not movements:
        raise HTTPException(status_code=404, detail="Nenhuma movimentação Encontrada!")
    return movements

#Consultar movimentação específica
@router.get("/stocks/movements/{id}", response_model=schemas.StockMovementOut)
def read_movement(id: int, db: Session = Depends(get_db)):
    movement = crud.get_stock_movement(db, id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movementação não Encontrada")
    return movement


#Consultar movimentação pelo id do produto
@router.get("/stocks/movements/product/{id}", response_model=list[schemas.StockMovementOut])
def read_movements_by_product(id: int, db: Session = Depends(get_db)):
    movement = crud.get_movements_by_product(db, id)
    if not movement:
        raise HTTPException(status_code=404, detail="Movementação não Encontrada")
    return movement