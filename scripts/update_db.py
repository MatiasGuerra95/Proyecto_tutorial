from flask_sqlalchemy import SQLAlchemy
from models import Contrato
from app import db

# Actualiza los contratos aquí
contratos = Contrato.query.filter(Contrato.pdf_path == None).all()
for contrato in contratos:
    contrato.pdf_path = 'pdfs/default_placeholder.pdf'
    db.session.add(contrato)

try:
    db.session.commit()
    print("Registros actualizados exitosamente.")
except Exception as e:
    db.session.rollback()
    print(f"Error al actualizar registros: {e}")

