import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajuste de rutas para importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture
def auth_headers():
    """Obtiene un token válido para las pruebas protegidas"""
    response = client.post("/token")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_crear_estacion(auth_headers):
    # Ahora enviamos auth_headers porque el endpoint está protegido
    response = client.post("/estaciones/", 
        json={"id": 1, "nombre": "Sede FISI", "ubicacion": "Lima"},
        headers=auth_headers
    )
    assert response.status_code == 201

def test_registrar_lecturas(auth_headers):
    # Enviamos el token para evitar el error 401
    client.post("/lecturas/", json={"estacion_id": 1, "valor": 50.0}, headers=auth_headers)
    client.post("/lecturas/", json={"estacion_id": 1, "valor": 100.0}, headers=auth_headers)
    response = client.post("/lecturas/", json={"estacion_id": 1, "valor": 75.0}, headers=auth_headers)
    
    assert response.status_code == 201 # Esto ahora será VERDE

def test_historial_y_promedio():
    # Los GET no están protegidos según tu código, pasan directo
    response = client.get("/estaciones/1/historial")
    data = response.json()
    assert data["conteo"] == 3
    assert data["promedio"] == 75.0

def test_dashboard_stats_ejecutivo():
    response = client.get("/estaciones/stats")
    stats = response.json()["estadisticas_globales"]
    assert stats["total_muestras_telemetria"] == 3
    assert stats["punto_critico_maximo"]["valor"] == 100.0