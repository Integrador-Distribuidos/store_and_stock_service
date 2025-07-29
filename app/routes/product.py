from app.schemas import product as schemas
from sqlalchemy.orm import Session
from app.crud import product as crud
from app.models import product_audit
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.database import get_db
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api")

'''def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()'''




# ------------------------
# ROTAS DE PRODUTOS
# ------------------------


#Cadastrar produto
@router.post("/products/", response_model=schemas.ProductOut)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)




#Consultar todos os produtos
@router.get("/products/", response_model=list[schemas.ProductOut])
def read_all_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)): 
    return crud.get_all_products_with_stock(db, skip, limit)


#Consultar produto específico
@router.get("/products/{id}", response_model=schemas.ProductOut)
def read_product(id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado!")
    return product


#Alterar produto
@router.put("/products/{id}", response_model=schemas.ProductOut)
def update_product(id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    return crud.update_product(db, id, product)


#Deletar produto
@router.delete("/products/{id}", response_model=schemas.ProductOut)
def delete_product(id: int, db: Session = Depends(get_db)):
    product = crud.delete_product(db, id)
    if not product:
        return JSONResponse(status_code=404, content={"detail": "Produto não Encontrado!"})
    return JSONResponse(content={"detail": "Produto Deletado!"})



@router.post("/products/{product_id}/upload-image/")
def upload_product_image_api(product_id: int,db: Session = Depends(get_db), file: UploadFile = File(...)):
    return crud.upload_product_image(product_id=product_id, db=db, file=file)

@router.get("/products/{product_id}/image-url")
def get_product_image_url_api(product_id: int, db: Session = Depends(get_db)):
    return crud.get_product_image_url(product_id=product_id, db=db)


@router.get("/auditoria/products")
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(product_audit.ProductAudit).all()



