# 🚀 FastAPI com Docker e PostgreSQL

Este projeto é uma API moderna e leve construída com **FastAPI**, containerizada com **Docker**, e conectada a um banco de dados **PostgreSQL** com persistência de dados.

---

## 📦 Tecnologias Utilizadas

- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Uvicorn](https://www.uvicorn.org/)

---

## ⚙️ Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/stock_service.git
cd stock_and_store_service

### 2. Crie um arquivo .env na mesma pasta do arquivo docker e defina as variáveis de ambiente
SECRET_KEY= #deve ser a mesma usada no serviço de usuarios em DJANGO_SECRET_KEY
ALGORITHM=HS256



.
stock_service Diretório principal da aplicação
├── app
│   # Pasta com as funções CRUD (Create, Read, Update, Delete)
│   ├── crud
│   │   ├── stock.py       # Funções para operações de estoque no banco (criar, buscar, atualizar, deletar)
│   │   ├── product.py     # Funções para persistência e recuperação de dados de produtos
│   │   └── movement.py    # Lógica de movimentações de estoque (entrada, saída, transferência)
│   │
│   # Pasta com as rotas/endpoints da API FastAPI
│   ├── routes
│   │   ├── stock.py       # Rotas relacionadas ao recurso "estoque" (GET, POST, etc.)
│   │   ├── product.py     # Rotas do recurso "produto"
│   │   └── movement.py    # Rotas para movimentações de produtos entre estoques
│   │
│   # Schemas Pydantic usados para validação e serialização de dados
│   ├── schemas
│   │   ├── stock.py       # Modelos de entrada/saída para operações de estoque
│   │   ├── product.py     # Modelos para criação e leitura de produtos
│   │   └── movement.py    # Schemas de movimentação de estoque (entrada, saída, transferência)
│   │
│   ├── main.py            # Ponto de entrada da aplicação FastAPI, configura e executa o app
│   ├── models.py          # Modelos ORM (SQLAlchemy) que representam as tabelas do banco de dados
│   ├── database.py        # Configuração da conexão com o banco de dados e criação da sessão
│   └── __init__.py        # Torna o diretório app um pacote Python (pode estar vazio)
│
# Arquivos de configuração e documentação
├── requirements.txt       # Lista de dependências Python necessárias para o projeto
├── Dockerfile             # Define a imagem Docker para a aplicação FastAPI
|__ .env                   # Defina as variáveis de ambiente
├── docker-compose.yml     # Arquivo de orquestração Docker para app + banco + outros serviços
└── README.md              # Documentação geral do projeto (setup, uso, contribuições etc.)




Endpoints da API

ESTOQUES
| Método | Endpoint                  | Descrição                              |
| ------ | ------------------------- | -------------------------------------- |
| POST   | `/api/stocks/`            | Criar um novo registro de estoque      |
| POST   | '/api/stocks/product/'    | Cadastrar um produto em um estoque     |
| GET    | `/api/stocks/`            | Listar todos os estoques               |
| GET    | `/api/stocks/{id}/`       | Detalhar um estoque específico         |
| GET    | `/api/stocks/store/{id}/` | Listar estoques de uma loja específica |
| PUT    | `/api/stocks/{id}/`       | Atualizar dados de um estoque          |
| DELETE | `/api/stocks/{id}/`       | Deletar um registro de estoque         |

PRODUTOS
| Método | Endpoint             | Descrição                       |
| ------ | -------------------- | ------------------------------- |
| POST   | `/api/products/`     | Criar novo produto              |
| GET    | `/api/products/`     | Listar todos os produtos        |
| GET    | `/api/products/{id}` | Detalhar um produto específico  |
| PUT    | `/api/products/{id}` | Atualizar um produto específico |
| DELETE | `/api/products/{id}` | Deletar um produto específico   |


MOVIMENTAÇÃO DE ESTOQUE
| Método | Endpoint                              | Descrição                                     |
| ------ | ------------------------------------- | --------------------------------------------- |
| POST   | `/api/stocks/movements/`              | Criar nova movimentação manual de estoque     |
| GET    | `/api/stocks/movements/`              | Listar todas as movimentações                 |
| GET    | `/api/stocks/movements/{id}/`         | Detalhar uma movimentação                     |
| GET    | `/api/stocks/movements/product/{id}/` | Listar movimentações de um produto específico |