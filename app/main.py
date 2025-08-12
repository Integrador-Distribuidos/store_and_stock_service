from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routes import movement, product, stock, orders, stores
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from sqlalchemy.orm import Session
from app.database import get_db
from prometheus_fastapi_instrumentator import Instrumentator
from app.models.models import Product, Stock, StockMovement
from app.models import store, order, order_item, audit_log
from app.database import SessionLocal
from app.audit import register_auditing_for_model
from app.dependencies.auth import AuthUserMiddleware

app = FastAPI(title="Serviço de Estoques")
Instrumentator().instrument(app).expose(app)

app.add_middleware(AuthUserMiddleware)

# Registra auditoria nos modelos
for model in [Product, Stock, StockMovement, store.Store, order.Order, order_item.OrderItem]:
    register_auditing_for_model(model, SessionLocal)



app.mount("/images", StaticFiles(directory="images"), name="images")

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Ambiente de desenvolvimento do Vite
        "https://server-stocks.stock2sell.shop",
        "https://integrador-distribuidos.github.io",
        "https://stock2sell.shop",
        "http://stock2sell.shop"  # Produção
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Cria as tabelas do banco
Base.metadata.create_all(bind=engine)

# Registra os routers
app.include_router(stock.router)
app.include_router(product.router)
app.include_router(movement.router)
app.include_router(orders.router)
app.include_router(stores.router)

@app.get("/auditoria")
def listar_auditorias(db: Session = Depends(get_db)):
    return db.query(audit_log.AuditLog).all()