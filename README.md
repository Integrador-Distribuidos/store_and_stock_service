
---

# 🚀 FastAPI com Docker e PostgreSQL

Este projeto é uma **API de gestão de estoques, produtos e movimentações** construída com **FastAPI**, containerizada com **Docker** e integrada a um banco de dados **PostgreSQL** com persistência de dados.

---

## 📦 Tecnologias Utilizadas

* [FastAPI](https://fastapi.tiangolo.com/) — Framework Python para APIs rápidas e assíncronas
* [PostgreSQL](https://www.postgresql.org/) — Banco de dados relacional robusto
* [Docker](https://www.docker.com/) — Containerização da aplicação
* [Docker Compose](https://docs.docker.com/compose/) — Orquestração de múltiplos serviços
* [Uvicorn](https://www.uvicorn.org/) — Servidor ASGI rápido para execução do FastAPI

---

## ⚙️ Como Executar

### 1️⃣ Clone o repositório

```bash
git clone https://github.com/seu-usuario/stock_service.git
cd stock_and_store_service
```

### 2️⃣ Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SECRET_KEY= # mesma usada no serviço de usuários (DJANGO_SECRET_KEY)
ALGORITHM=HS256
DATABASE_URL=postgresql://postgres:admin@localhost/postgres
BASE_URL=http://localhost:8000
```

### 3️⃣ Suba os containers

```bash
docker-compose up --build
```

A API ficará disponível em:

```
http://localhost:8000
```

A documentação interativa do Swagger estará em:

```
http://localhost:8000/docs
```

---

## 📂 Estrutura do Projeto

```
stock_service/
├── app/
│   ├── crud/
│   │   ├── stock.py       # CRUD de estoques
│   │   ├── product.py     # CRUD de produtos
│   │   └── movement.py    # CRUD de movimentações
│   │
│   ├── routes/
│   │   ├── stock.py       # Endpoints de estoques
│   │   ├── product.py     # Endpoints de produtos
│   │   └── movement.py    # Endpoints de movimentações
│   │
│   ├── schemas/
│   │   ├── stock.py       # Schemas Pydantic para estoques
│   │   ├── product.py     # Schemas para produtos
│   │   └── movement.py    # Schemas para movimentações
│   │
│   ├── main.py            # Ponto de entrada da aplicação
│   ├── models.py          # Modelos ORM (SQLAlchemy)
│   ├── database.py        # Conexão com o banco
│   └── __init__.py
│
├── requirements.txt       # Dependências Python
├── Dockerfile             # Configuração da imagem Docker
├── docker-compose.yml     # Orquestração de serviços
├── .env                   # Variáveis de ambiente
└── README.md              # Documentação do projeto
```

---

## 🔗 Endpoints da API

### 📦 Estoques

| Método     | Endpoint                  | Descrição                              |
| ---------- | ------------------------- | -------------------------------------- |
| **POST**   | `/api/stocks/`            | Criar um novo estoque                  |
| **POST**   | `/api/stocks/product/`    | Cadastrar um produto em um estoque     |
| **GET**    | `/api/stocks/`            | Listar todos os estoques               |
| **GET**    | `/api/stocks/{id}/`       | Detalhar um estoque específico         |
| **GET**    | `/api/stocks/store/{id}/` | Listar estoques de uma loja específica |
| **PUT**    | `/api/stocks/{id}/`       | Atualizar dados de um estoque          |
| **DELETE** | `/api/stocks/{id}/`       | Deletar um estoque                     |

---

### 🛒 Produtos

| Método     | Endpoint              | Descrição                      |
| ---------- | --------------------- | ------------------------------ |
| **POST**   | `/api/products/`      | Criar um novo produto          |
| **GET**    | `/api/products/`      | Listar todos os produtos       |
| **GET**    | `/api/products/{id}/` | Detalhar um produto específico |
| **PUT**    | `/api/products/{id}/` | Atualizar um produto           |
| **DELETE** | `/api/products/{id}/` | Deletar um produto             |

---

### 🔄 Movimentações de Estoque

| Método   | Endpoint                              | Descrição                                     |
| -------- | ------------------------------------- | --------------------------------------------- |
| **POST** | `/api/stocks/movements/`              | Criar nova movimentação manual de estoque     |
| **GET**  | `/api/stocks/movements/`              | Listar todas as movimentações                 |
| **GET**  | `/api/stocks/movements/{id}/`         | Detalhar uma movimentação                     |
| **GET**  | `/api/stocks/movements/product/{id}/` | Listar movimentações de um produto específico |

---