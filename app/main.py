from fastapi import FastAPI
from app.routes import movement, product, stock, orders, stores
from app.database import engine, Base

app = FastAPI(title="Serviço de Estoques")

Base.metadata.create_all(bind=engine)

app.include_router(stock.router)
app.include_router(product.router)
app.include_router(movement.router)
app.include_router(orders.router)
app.include_router(stores.router)
