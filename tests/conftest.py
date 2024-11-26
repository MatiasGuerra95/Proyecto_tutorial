import os
import pytest
from app import app, db
from models import Trabajador, Contrato

@pytest.fixture
def client():
    """Fixture para configurar el cliente de pruebas."""
    os.environ["FLASK_ENV"] = "testing"
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Base de datos en memoria para pruebas
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Crear todas las tablas en la base de datos de prueba
            yield client  # Proporcionar el cliente para las pruebas
            db.session.remove()  # Limpiar la sesión
            db.drop_all()  # Eliminar todas las tablas

@pytest.fixture
def setup_data():
    """Fixture para crear datos de prueba en la base de datos."""
    # Crear trabajadores de prueba
    trabajador1 = Trabajador(nombre="Juan", apellidop="Pérez", rut="19000000-1")
    trabajador2 = Trabajador(nombre="Ana", apellidop="Gómez", rut="20000000-2")

    # Crear contratos de prueba
    contrato1 = Contrato(trabajador_id=1, fecha_inicio="2024-01-01", fecha_termino="2024-12-31", pdf_path="pdfs/contrato1.pdf")
    contrato2 = Contrato(trabajador_id=2, fecha_inicio="2024-02-01", fecha_termino="2024-12-31", pdf_path="pdfs/contrato2.pdf")

    # Añadir a la sesión
    db.session.add_all([trabajador1, trabajador2, contrato1, contrato2])
    db.session.commit()


