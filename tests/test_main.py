from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Verifica que el endpoint principal responda 200 OK y tenga la estructura correcta"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "visits" in data
    # No validamos el número exacto de visitas porque depende de Redis,
    # y en tests unitarios aislados Redis podría no estar presente o estar vacío.

def test_health_check():
    """Verifica el endpoint de salud (vital para Kubernetes)"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"