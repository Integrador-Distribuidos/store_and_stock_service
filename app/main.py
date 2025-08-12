from fastapi import FastAPI, Depends, logger
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
from app.models.request_logs import RequestLog
import time
from datetime import datetime
from fastapi import FastAPI, Request
import logging
from sqlalchemy import event


app = FastAPI(title="Serviço de Estoques")
Instrumentator().instrument(app).expose(app)


#----------------------------------------------------
 

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    query_count = 0  # contador local

    # Listener para contar queries SQL
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)

    # Executa requisição
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # ms

    # Remove listener para evitar contagem acumulada entre requisições
    event.remove(engine, "before_cursor_execute", before_cursor_execute)

    # Log no console
    logger.info(
        f"{request.method} {request.url.path} - {process_time:.2f} ms - {query_count} queries"
    )

    # Adiciona no header da resposta
    response.headers["X-Process-Time-ms"] = str(round(process_time, 2))
    response.headers["X-Query-Count"] = str(query_count)

    # Salva no banco
    db: Session = SessionLocal()
    try:
        log_entry = RequestLog(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
            query_count=query_count,
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar log no banco: {e}")
        db.rollback()
    finally:
        db.close()

    return response


#-------------------------------------------------------------------

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