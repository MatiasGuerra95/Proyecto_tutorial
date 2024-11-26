from unittest.mock import Mock, patch
import pytest
from app import app

@pytest.fixture
def login(client):
    """Función auxiliar para iniciar sesión en pruebas."""
    client.post('/login', data={'username': 'test_user', 'password': 'test_password'})

def test_home_page(client):
    """Test para la página principal."""
    response = client.get("/")
    assert response.status_code == 302  # Redirección esperada
    assert "trabajador" in response.location  # Redirige a lista de trabajadores

def test_lista_contrato(client):
    """Test para la ruta de lista de contratos."""
    response = client.get("/contrato")
    assert response.status_code == 200
    assert b"Lista de Contratos" in response.data

def test_crear_contrato(client):
    """Test para la creación de un contrato."""
    response = client.get("/contrato/crear_contrato")
    assert response.status_code == 200
    assert b"Crear Contrato" in response.data

def test_ruta_inexistente(client):
    """Test para una ruta inexistente."""
    response = client.get("/ruta_que_no_existe")
    assert response.status_code == 404

