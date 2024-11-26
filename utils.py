from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import logging
import os
import bleach

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

# Directorio de PDFs
PDF_FOLDER = os.path.join('static', 'pdfs')

def sanitize_input(data):
    """
    Sanitiza los datos de entrada para evitar inyecciones de HTML o scripts.
    Utiliza bleach para limpiar cadenas de texto.
    """
    if isinstance(data, str):
        return bleach.clean(data, strip=True)
    return data

def generar_pdf(trabajador, fecha_inicio, fecha_termino):
    """
    Genera un archivo PDF de contrato para un trabajador especificado.
    
    Args:
        trabajador: Objeto del modelo Trabajador, debe contener al menos los atributos 'rut', 'nombre' y 'apellidop'.
        fecha_inicio (str): Fecha de inicio del contrato.
        fecha_termino (str): Fecha de término del contrato (opcional).

    Returns:
        str: Nombre del archivo PDF generado o None si ocurre un error.
    """
    try:
        # Validar datos críticos
        if not trabajador or not getattr(trabajador, 'rut', None):
            logger.error("No se proporcionó un trabajador válido o el RUT está ausente.")
            return None
        if not fecha_inicio:
            logger.error("No se proporcionó una fecha de inicio para el contrato.")
            return None

        # Crear la carpeta de destino si no existe
        os.makedirs(PDF_FOLDER, exist_ok=True)

        # Sanitizar datos
        rut = sanitize_input(trabajador.rut)
        nombre = sanitize_input(trabajador.nombre)
        apellido = sanitize_input(trabajador.apellidop)
        fecha_inicio = sanitize_input(str(fecha_inicio))
        fecha_termino = sanitize_input(str(fecha_termino)) if fecha_termino else 'Indefinido'

        # Nombre y ruta del archivo PDF
        pdf_filename = f"contrato_{rut}_{fecha_inicio}.pdf"
        pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

        # Eliminar el PDF existente si ya existe
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logger.info(f"PDF existente eliminado: {pdf_path}")

        # Crear el PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setFont("Helvetica", 12)

        # Añadir contenido al PDF
        c.drawString(100, 800, f"Contrato de Trabajo")
        c.drawString(100, 780, f"Trabajador: {nombre} {apellido}")
        c.drawString(100, 760, f"RUT: {rut}")
        c.drawString(100, 740, f"Fecha de Inicio: {fecha_inicio}")
        c.drawString(100, 720, f"Fecha de Término: {fecha_termino}")
        c.drawString(100, 700, "Este documento representa un contrato de trabajo válido.")
        c.save()

        # Log de éxito
        logger.info(f"PDF generado exitosamente para el trabajador con RUT {rut} en: {pdf_path}")
        return pdf_filename
    except Exception as e:
        # Log de error detallado
        logger.error(f"Error al generar el PDF para el trabajador con RUT {getattr(trabajador, 'rut', 'desconocido')}: {e}")
        return None


