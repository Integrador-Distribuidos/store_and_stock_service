from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import movement, product, stock, orders, stores
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import product_audit, stock_audit, stock_movement_audit
import os

app = FastAPI(title="Serviço de Estoques")

os.makedirs('images', exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Porta padrão do Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas do banco
Base.metadata.create_all(bind=engine)

# Registra os routers
app.include_router(stock.router)
app.include_router(product.router)
app.include_router(movement.router)
app.include_router(orders.router)
app.include_router(stores.router)

@app.get("/auditoria/products")
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(product_audit.ProductAudit).all()

#Exibir auditoria
@app.get("/auditoria/stocks")
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(stock_audit.StockAudit).all()

@app.get("/auditoria/movements")
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(stock_movement_audit.StockMovementAudit).all()