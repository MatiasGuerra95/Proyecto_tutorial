from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def generar_placeholder_pdf():
    pdf_folder = os.path.join('static', 'pdfs')
    os.makedirs(pdf_folder, exist_ok=True)
    pdf_path = os.path.join(pdf_folder, 'default_placeholder.pdf')
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.drawString(100, 800, "Este contrato no tiene un archivo PDF asociado.")
    c.save()
    print(f"PDF de marcador generado en {pdf_path}")

if __name__ == "__main__":
    generar_placeholder_pdf()
