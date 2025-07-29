from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import movement, product, stock, orders, stores
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base

app = FastAPI(title="Serviço de Estoques")


# Monta o diretório "images" na rota "/images"
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

