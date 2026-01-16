from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

# Creamos un cliente de prueba
client = TestClient(app)

# MOCK: Simulamos la respuesta de Redis para no necesitar una BD real corriendo
def test_read_root():
    # "Parcheamos" el objeto 'r' (redis) dentro de main.py
    with patch("app.main.r") as mock_redis:
        # Configuramos el mock para que cuando llamen a .incr() devuelva 5
        mock_redis.incr.return_value = 5
        
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["visits"] == 5  # Verificamos que usó nuestro valor simulado
        assert "app" in data

def test_health_check():
    with patch("app.main.r") as mock_redis:
        # Simulamos que el ping responde True
        mock_redis.ping.return_value = True
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["redis"] is True