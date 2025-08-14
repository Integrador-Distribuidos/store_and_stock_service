from dotenv import load_dotenv
import pytest
import httpx
import os
import uuid
from generate_jwt import create_test_token

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
AUTH_TOKEN = create_test_token()
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

def generate_unique_cnpj(suffix_hex: str) -> str:
    # Converte 2 chars hex para número decimal 2 dígitos (ex: 'fe' -> '254')
    suffix_num = int(suffix_hex, 16)
    return f"00.000.000/0001-{suffix_num:02d}"


@pytest.fixture
def new_product_data():
    unique_id = uuid.uuid4().hex[:6]
    return {
        "name": f"Produto Teste {unique_id}",
        "image": "",
        "description": "Descrição detalhada",
        "price": 345,
        "sku": "SKU qualquer",
        "category": "Categoria",
        "quantity": 45,
        "creation_date": "2025-08-14",
        "id_stock": 57
    }


@pytest.fixture
def test_create_store(new_product_data):
    data = new_product_data
    created_products = []

    # Cria 300 produtos
    for i in range(300):
        # Gera um nome único para cada produto
        unique_id = uuid.uuid4().hex[:6]
        data["name"] = f"Produto Teste {unique_id}"

        response = httpx.post(
            f"{BASE_URL}/api/products/",
            json=data,  # envia como JSON, não form-data
            headers=HEADERS
        )
        assert response.status_code in (200, 201), f"Falha ao criar produto: {response.text}"
        created_products.append(response.json())

    return created_products  # retorna lista de produtos criados


@pytest.fixture
def new_store_data():
    unique_id = uuid.uuid4().hex[:6]
    cnpj = generate_unique_cnpj(unique_id[:2])
    return {
        "name": f"Loja Teste {unique_id}",
        "cnpj": cnpj,
        "creation_date": "2025-08-10",
        "email": f"teste{unique_id}@loja.com",
        "phone_number": "+5511999999999"
    }




@pytest.fixture
def create_store(new_store_data):
    data = new_store_data

    # Envio multipart/form-data sem arquivo:
    response = httpx.post(
        f"{BASE_URL}/api/stores/",
        data=data,
        headers=HEADERS
    )

    # Se quiser enviar arquivo, descomente abaixo:
    # with open("tests/assets/logo.png", "rb") as f:
    #     files = {"image": ("logo.png", f, "image/png")}
    #     response = httpx.post(
    #         f"{BASE_URL}/api/stores/",
    #         data=data,
    #         files=files,
    #         headers=HEADERS
    #     )

    assert response.status_code in (200, 201), f"Falha ao criar store: {response.text}"
    store = response.json()
    yield store
    # Cleanup: deleta a store criada
    httpx.delete(f"{BASE_URL}/api/stores/{store['id_store']}", headers=HEADERS)

def test_create_store(new_store_data):
    response = httpx.post(f"{BASE_URL}/api/stores/", data=new_store_data, headers=HEADERS)
    assert response.status_code in (200, 201), f"Falha no create_store: {response.text}"
    data = response.json()
    assert data["name"] == new_store_data["name"]
    assert "id_store" in data

def test_read_store(create_store):
    store_id = create_store["id_store"]
    response = httpx.get(f"{BASE_URL}/api/stores/{store_id}", headers=HEADERS)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["id_store"] == store_id

def test_update_store(create_store):
    store_id = create_store["id_store"]
    update_data = {"name": "Loja Atualizada"}
    response = httpx.put(f"{BASE_URL}/api/stores/{store_id}", json=update_data, headers=HEADERS)
    assert response.status_code in (200, 201)
    data = response.json()
    assert data["name"] == "Loja Atualizada"

def test_delete_store():
    unique_id = uuid.uuid4().hex[:6]
    cnpj = generate_unique_cnpj(unique_id[:2])
    new_store = {
        "name": f"Loja Para Deletar {unique_id}",
        "cnpj": cnpj,
        "creation_date": "2025-08-10",
        "email": f"delete{unique_id}@loja.com",
        "phone_number": "+5511988888888"
    }
    create_resp = httpx.post(f"{BASE_URL}/api/stores/", data=new_store, headers=HEADERS)
    assert create_resp.status_code in (200, 201), f"Falha ao criar store para delete: {create_resp.text}"
    store_id = create_resp.json()["id_store"]

    delete_resp = httpx.delete(f"{BASE_URL}/api/stores/{store_id}", headers=HEADERS)
    assert delete_resp.status_code in (200, 204), f"Falha ao deletar store: {delete_resp.text}"

    get_resp = httpx.get(f"{BASE_URL}/api/stores/{store_id}", headers=HEADERS)
    assert get_resp.status_code == 404
