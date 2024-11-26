import os
from unittest.mock import Mock, patch
from utils import sanitize_input, generar_pdf

def test_sanitize_input():
    """Test para sanitizar cadenas de texto."""
    assert sanitize_input("<script>alert('hack');</script>") == "alert('hack');"
    assert sanitize_input("<b>Texto</b>") == "Texto"
    assert sanitize_input("Texto limpio") == "Texto limpio"
    assert sanitize_input(None) is None  # Manejo de entradas no string

@patch("os.makedirs")
@patch("utils.canvas.Canvas")
def test_generar_pdf(mock_canvas, mock_makedirs):
    """Test para la generación de PDFs."""
    # Simular un trabajador válido
    trabajador = Mock(rut="19000000-1")

    # Caso exitoso
    pdf_filename = generar_pdf(trabajador, "2024-01-01", "2024-12-31")
    assert pdf_filename == "contrato_19000000-1_2024-01-01.pdf"
    mock_canvas.assert_called_once()
    mock_makedirs.assert_called_once_with(os.path.join('static', 'pdfs'), exist_ok=True)

    # Caso: trabajador inválido
    assert generar_pdf(None, "2024-01-01", "2024-12-31") is None

    # Caso: fecha de inicio inválida
    assert generar_pdf(trabajador, None, "2024-12-31") is None
