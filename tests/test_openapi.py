# tests/test_openapi.py
from dotenv import load_dotenv
import httpx
import pytest
import json
from termcolor import colored
from generate_jwt import create_test_token
import os
load_dotenv()

AUTH_TOKEN = create_test_token()
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def openapi():
    r = httpx.get(f"{BASE_URL}/openapi.json")
    r.raise_for_status()
    return r.json()

def pretty_print_result(method, url, status_code, response_text):
    color = "green" if status_code < 400 else "yellow" if status_code < 500 else "red"
    print(colored(f"\n[{method}] {url} -> {status_code}", color))
    print(colored(f"Response:", "cyan"))
    print(response_text[:500] + ("..." if len(response_text) > 500 else ""))

def test_all_endpoints(openapi):
    paths = openapi["paths"]
    for path, methods in paths.items():
        for method, details in methods.items():
            url = f"{BASE_URL}{path}"
            headers = {}

            # Verifica se o endpoint precisa de segurança (exemplo básico)
            if "security" in details and details["security"]:
                headers = HEADERS

            print(f"\n🔍 Testando {method.upper()} {url} com headers {headers}")

            if method == "get":
                r = httpx.get(url, headers=headers)
            elif method in ["post", "put", "patch"]:
                r = httpx.request(method.upper(), url, json={}, headers=headers)
            elif method == "delete":
                r = httpx.delete(url, headers=headers)
            else:
                print(f"⚠ Método {method.upper()} não suportado.")
                continue

            print(f"📡 Status: {r.status_code}")
            try:
                print(f"📄 Resposta: {r.json()}")
            except Exception:
                print(f"📄 Resposta (texto): {r.text}")

            assert r.status_code < 500, f"❌ Erro no endpoint {method.upper()} {url}"