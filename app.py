from werkzeug.utils import secure_filename
from venv import logger
from flask import Flask, render_template, redirect, url_for, flash, jsonify, send_from_directory, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from forms import BancoForm, TrabajadorForm, ContratoForm, DiaContratoForm, AfpForm, ComunaForm, CuentaForm, PaisForm, PrevisionForm, RegionForm, Estado_CivilForm, GeneroForm, SucursalForm, DiaJornadaForm, JornadaForm, ClienteForm ,RepresentanteForm, ProyectoForm, ServicioForm, EmpresaForm, PlataformaForm, CausalContratacionForm
from models import Bancos, Trabajador, Contrato, DiaContrato, Afp, Comuna, Tipo_cuenta, Pais, Prev_salud, Region, Estado_Civil, Genero, FormaPago, Sucursal, Cliente, Jornada, DiaJornada, RolFirmaContratos, Representante, Proyecto, Servicio, Empresa, Plataforma, CausalContratacion
from utils import generar_pdf, sanitize_input
from datetime import datetime
import os
import time
import bleach
import logging
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from flask_wtf.csrf import CSRFProtect, generate_csrf
from extensions import db, migrate, csrf

# Configuración básica de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar las variables de entorno
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.getLogger('flask_wtf.csrf').setLevel(logging.DEBUG)

# Inicializar extensiones con la aplicación
csrf.init_app(app)
db.init_app(app)
migrate.init_app(app, db)

# Context Processor para inyectar CSRF token en todas las plantillas
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Función para sanitizar datos en rutas específicas si es necesario
def sanitize_input(data):
    if isinstance(data, str):
        return bleach.clean(data)
    return data

def wait_for_db(max_retries=5, delay=5):
    retries = max_retries
    while retries > 0:
        try:
            app.logger.info("Intentando guardar la jornada en la base de datos...")
            with app.app_context():
                db.session.execute('SELECT 1')
            logger.info('¡Conexión exitosa a la base de datos!')
            return
        except OperationalError as e:
            retries -= 1
            logger.warning(f'Error al conectar a la base de datos: {e}. Reintentando en {delay} segundos...')
            time.sleep(delay)
    logger.error('No se pudo conectar a la base de datos después de varios intentos.')
    raise Exception('No se pudo conectar a la base de datos.')


# Manejo de archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f'Error 404: {error}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Error 500: {error}')
    db.session.rollback()
    return render_template('500.html'), 500

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}


@app.route('/')
def index():
    return redirect(url_for('lista_trabajador'))  # Redirige a la lista de trabajadores en la página de inicio

@app.route('/trabajador', methods=['GET', 'POST'])
def lista_trabajador():
    form = TrabajadorForm()

    # Definir las opciones de los campos select en el formulario
    form.afp_id.choices = [(afp.id, afp.nombre) for afp in Afp.query.all()]
    form.banco_id.choices = [(banco.id, banco.nombre) for banco in Bancos.query.all()]
    form.comuna_id.choices = [(comuna.id, comuna.nombre) for comuna in Comuna.query.all()]
    form.banco_tipo_cuenta_id.choices = [(banco_tipo_cuenta.id, banco_tipo_cuenta.nombre) for banco_tipo_cuenta in Tipo_cuenta.query.all()]
    form.pais_id.choices = [(pais.id, pais.nombre) for pais in Pais.query.all()]
    form.prev_salud_id.choices = [(prev_salud.id, prev_salud.nombre) for prev_salud in Prev_salud.query.all()]
    form.estado_civil_id.choices = [(estado_civil.id, estado_civil.estado) for estado_civil in Estado_Civil.query.all()]
    form.genero_id.choices = [(genero.id, genero.genero) for genero in Genero.query.all()]
    form.region_id.choices = [(region.id, region.region) for region in Region.query.all()]
    form.forma_pago_id.choices = [(forma.id, forma.nombre) for forma in FormaPago.query.all()]

    if request.method == 'POST':
        trabajador_id = request.form.get('trabajador_id')  # Obtener el ID del trabajador

        # Validar el formulario
        if form.validate_on_submit():
            try:
                if trabajador_id:  # Caso editar
                    trabajador = Trabajador.query.get_or_404(trabajador_id)

                    # Actualizar todos los campos del trabajador
                    trabajador.rut = form.rut.data
                    trabajador.nombre = form.nombre.data
                    trabajador.apellidop = form.apellidop.data
                    trabajador.apellidom = form.apellidom.data
                    trabajador.email = form.email.data
                    trabajador.telefono = form.telefono.data
                    trabajador.direccion_calle = form.direccion_calle.data
                    trabajador.direccion_numero = form.direccion_numero.data
                    trabajador.direccion_dpto = form.direccion_dpto.data
                    trabajador.fecha_nacimiento = form.fecha_nacimiento.data
                    trabajador.pais_id = form.pais_id.data
                    trabajador.genero_id = form.genero_id.data
                    trabajador.estado_civil_id = form.estado_civil_id.data
                    trabajador.region_id = form.region_id.data
                    trabajador.comuna_id = form.comuna_id.data
                    trabajador.forma_pago_id = form.forma_pago_id.data
                    trabajador.banco_id = form.banco_id.data
                    trabajador.banco_tipo_cuenta_id = form.banco_tipo_cuenta_id.data
                    trabajador.banco_cuenta_numero = form.banco_cuenta_numero.data
                    trabajador.afp_id = form.afp_id.data
                    trabajador.prev_salud_id = form.prev_salud_id.data

                    flash("Trabajador actualizado exitosamente.", "success")
                else:  # Caso agregar
                    # Crear un nuevo trabajador con todos los campos del formulario
                    nuevo_trabajador = Trabajador(
                        rut=form.rut.data,
                        nombre=form.nombre.data,
                        apellidop=form.apellidop.data,
                        apellidom=form.apellidom.data,
                        email=form.email.data,
                        telefono=form.telefono.data,
                        direccion_calle=form.direccion_calle.data,
                        direccion_numero=form.direccion_numero.data,
                        direccion_dpto=form.direccion_dpto.data,
                        fecha_nacimiento=form.fecha_nacimiento.data,
                        pais_id=form.pais_id.data,
                        genero_id=form.genero_id.data,
                        estado_civil_id=form.estado_civil_id.data,
                        region_id=form.region_id.data,
                        comuna_id=form.comuna_id.data,
                        forma_pago_id=form.forma_pago_id.data,
                        banco_id=form.banco_id.data,
                        banco_tipo_cuenta_id=form.banco_tipo_cuenta_id.data,
                        banco_cuenta_numero=form.banco_cuenta_numero.data,
                        afp_id=form.afp_id.data,
                        prev_salud_id=form.prev_salud_id.data
                    )
                    db.session.add(nuevo_trabajador)
                    flash("Trabajador agregado exitosamente.", "success")

                # Guardar cambios en la base de datos
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                flash(f"Error al guardar el trabajador: {e}", "danger")
                app.logger.error(f"Error al guardar el trabajador: {e}")

            # Redirigir de vuelta a la lista de trabajadores
            return redirect(url_for('lista_trabajador'))
        else:
            flash("Por favor, corrige los errores en el formulario.", "danger")
            app.logger.warning(f"Errores de validación en TrabajadorForm: {form.errors}")

    # GET request: Renderizar la lista de trabajadores
    trabajadores = Trabajador.query.all()

    return render_template(
        'lista_trabajador.html',
        trabajadores=trabajadores,
        form=form
    )

#@app.route('/trabajador/crear_trabajador', methods=['GET', 'POST'])
#def crear_trabajador():
    form = TrabajadorForm()

    # Definir las opciones de los campos select en el formulario
    form.afp_id.choices = [(afp.id, afp.nombre) for afp in Afp.query.all()]
    form.banco_id.choices = [(banco.id, banco.nombre) for banco in Bancos.query.all()]
    form.comuna_id.choices = [(comuna.id, comuna.nombre) for comuna in Comuna.query.all()]
    form.banco_tipo_cuenta_id.choices = [(banco_tipo_cuenta.id, banco_tipo_cuenta.nombre) for banco_tipo_cuenta in Tipo_cuenta.query.all()]
    form.pais_id.choices = [(pais.id, pais.nombre) for pais in Pais.query.all()]
    form.prev_salud_id.choices = [(prev_salud.id, prev_salud.nombre) for prev_salud in Prev_salud.query.all()]
    form.estado_civil_id.choices = [(estado_civil.id, estado_civil.estado) for estado_civil in Estado_Civil.query.all()]
    form.genero_id.choices = [(genero.id, genero.genero) for genero in Genero.query.all()]
    form.region_id.choices = [(region.id, region.region) for region in Region.query.all()]
    form.forma_pago_id.choices = [(forma.id, forma.nombre) for forma in FormaPago.query.all()]    

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        form.sanitize_data()
        # Crear un nuevo trabajador con los datos del formulario
        nuevo_trabajador = Trabajador(
            rut=sanitize_input(form.rut.data),
            nombre=sanitize_input(form.nombre.data),
            apellidop=sanitize_input(form.apellidop.data),
            apellidom=sanitize_input(form.apellidom.data),
            fecha_nacimiento=sanitize_input(form.fecha_nacimiento.data),
            pais_id=sanitize_input(form.pais_id.data),
            genero_id=sanitize_input(form.genero_id.data),
            estado_civil_id=sanitize_input(form.estado_civil_id.data),
            direccion_calle=sanitize_input(form.direccion_calle.data),
            direccion_numero=sanitize_input(form.direccion_numero.data),
            direccion_dpto=sanitize_input(form.direccion_dpto.data),
            region_id=sanitize_input(form.region_id.data),
            comuna_id=sanitize_input(form.comuna_id.data),
            email=sanitize_input(form.email.data),
            telefono=sanitize_input(form.telefono.data),
            forma_pago_id=sanitize_input(form.forma_pago_id.data),
            banco_id=sanitize_input(form.banco_id.data),
            banco_tipo_cuenta_id=sanitize_input(form.banco_tipo_cuenta_id.data),
            banco_cuenta_numero=sanitize_input(form.banco_cuenta_numero.data),
            afp_id=sanitize_input(form.afp_id.data),
            prev_salud_id=sanitize_input(form.prev_salud_id.data)
        )
        try:
            db.session.add(nuevo_trabajador)
            db.session.commit()
            return jsonify({"message": "Trabajador creado exitosamente", "status": "success"}), 200
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"message": f"Error al crear el trabajador: {e}", "status": "error"}), 500

    return jsonify({"message": "Errores en el formulario", "errors": form.errors, "status": "error"}), 400


@app.route('/trabajador/detalle/<int:id>', methods=['GET'])
def trabajador_detalle(id):
    trabajador = Trabajador.query.get_or_404(id)
    data = {
        "rut": trabajador.rut,
        "nombre": trabajador.nombre,
        "apellidop": trabajador.apellidop,
        "apellidom": trabajador.apellidom,
        "fecha_nacimiento": trabajador.fecha_nacimiento.strftime('%Y-%m-%d') if trabajador.fecha_nacimiento else "",
        "pais_id": trabajador.pais_id,
        "genero_id": trabajador.genero_id,
        "estado_civil_id": trabajador.estado_civil_id,
        "direccion_calle": trabajador.direccion_calle,
        "direccion_numero": trabajador.direccion_numero,
        "direccion_dpto": trabajador.direccion_dpto,
        "region_id": trabajador.region_id,
        "comuna_id": trabajador.comuna_id,
        "email": trabajador.email,
        "telefono": trabajador.telefono,
        "forma_pago_id": trabajador.forma_pago_id,
        "banco_id": trabajador.banco_id,
        "banco_tipo_cuenta_id": trabajador.banco_tipo_cuenta_id,
        "banco_cuenta_numero": trabajador.banco_cuenta_numero,
        "afp_id": trabajador.afp_id,
        "prev_salud_id": trabajador.prev_salud_id
    }
    return jsonify(data)

@app.route('/delete_trabajador/<int:trabajador_id>', methods=['POST'])
def delete_trabajador(trabajador_id):
    trabajador = Trabajador.query.get_or_404(trabajador_id)
    
    # Comprobar si el trabajador tiene contratos
    if trabajador.contratos:  # `contratos` es el nombre de la relación en el modelo
        flash("El trabajador no puede ser eliminado, porque tiene un contrato vigente.", "danger")
        app.logger.warning(f"Intento de eliminación de trabajador con contratos: ID {trabajador_id}")
        return redirect(url_for('lista_trabajador'))
    
    try:
        db.session.delete(trabajador)
        db.session.commit()
        flash("Trabajador eliminado exitosamente.", "success")
        app.logger.info(f"Trabajador con ID {trabajador_id} eliminado exitosamente.")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error al eliminar el trabajador.", "danger")
        app.logger.error(f"Error al eliminar el trabajador con ID {trabajador_id}: {e}")

    return redirect(url_for('lista_trabajador'))


@app.route('/opciones_selectores')
def opciones_selectores():
    bancos = [{"id": banco.id, "nombre": banco.nombre} for banco in Bancos.query.all()]
    tipos_cuenta = [{"id": tipo.id, "nombre": tipo.nombre} for tipo in Tipo_cuenta.query.all()]
    afps = [{"id": afp.id, "nombre": afp.nombre} for afp in Afp.query.all()]
    previsiones_salud = [{"id": prev.id, "nombre": prev.nombre} for prev in Prev_salud.query.all()]
    generos = [{"id": genero.id, "genero": genero.genero} for genero in Genero.query.all()]
    estados_civiles = [{"id": estado.id, "estado": estado.estado} for estado in Estado_Civil.query.all()]
    paises = [{"id": pais.id, "nombre": pais.nombre} for pais in Pais.query.all()]
    regiones = [{"id": region.id, "region": region.region} for region in Region.query.all()]
    comunas = [{"id": comuna.id, "nombre": comuna.nombre, "region_id": comuna.region_id} for comuna in Comuna.query.all()]
    forma_pago = [{"id": forma.id, "nombre": forma.nombre} for forma in FormaPago.query.all()]

    return jsonify({
        "bancos": bancos,
        "tipos_cuenta": tipos_cuenta,
        "afps": afps,
        "previsiones_salud": previsiones_salud,
        "generos": generos,
        "estados_civiles": estados_civiles,
        "paises": paises,
        "regiones": regiones,
        "comunas": comunas,
        "forma_pago": forma_pago        
    })


@app.route('/contrato', methods=['GET', 'POST'])
def lista_contrato():
    form = ContratoForm()

    # Consultar listas para los select
    trabajadores = Trabajador.query.all()
    empresas_mvs = Empresa.query.all()
    clientes = Cliente.query.all()
    servicios = Servicio.query.all()
    sucursales = Sucursal.query.all()
    representantes = Representante.query.all()
    
    # Si tu lógica para validador y firmante es similar:
    # validadores = Validador.query.all()  # Si existe un modelo Validador
    # firmantes = Firmante.query.all()      # Si existe un modelo Firmante
    # O si no los tienes, puedes dejarlos vacíos o usar trabajadores filtrados
    #validadores = trabajadores  # Placeholder hasta definir la lógica real
    #firmantes = trabajadores    # Placeholder hasta definir la lógica real

    form.trabajador_id.choices = [
        (t.id, f"{t.nombre} {t.apellidop}") for t in trabajadores
    ]

    if request.method == 'POST':
        contrato_id = request.form.get('id')  
        if contrato_id:
            # Editar Contrato
            contrato = Contrato.query.get_or_404(contrato_id)
            if form.validate_on_submit():
                contrato.trabajador_id = form.trabajador_id.data
                contrato.fecha_inicio = form.fecha_inicio.data
                contrato.fecha_termino = form.fecha_termino.data

                try:
                    db.session.commit()
                    pdf_filename = generar_pdf(contrato.trabajador, contrato.fecha_inicio, contrato.fecha_termino)
                    if pdf_filename:
                        contrato.pdf_path = pdf_filename
                        db.session.commit()
                        flash("Contrato actualizado y PDF generado exitosamente.", "success")
                    else:
                        flash("Contrato actualizado pero falló la generación del PDF.", "warning")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    flash(f"Error al actualizar el contrato: {e}", "danger")
                except Exception as e:
                    flash(f"Error al generar el PDF del contrato: {e}", "danger")
            else:
                flash("Por favor, corrige los errores en el formulario.", "danger")
        else:
            # Crear Contrato
            if form.validate_on_submit():
                trabajador_id = form.trabajador_id.data
                fecha_inicio = form.fecha_inicio.data
                fecha_termino = form.fecha_termino.data

                trabajador = Trabajador.query.get(trabajador_id)
                if not trabajador:
                    flash("El trabajador seleccionado no existe.", "danger")
                    return redirect(url_for("lista_contrato"))

                nuevo_contrato = Contrato(
                    trabajador_id=trabajador_id,
                    fecha_inicio=fecha_inicio,
                    fecha_termino=fecha_termino,
                )

                try:
                    db.session.add(nuevo_contrato)
                    db.session.commit()
                    pdf_filename = generar_pdf(trabajador, fecha_inicio, fecha_termino)
                    if pdf_filename:
                        nuevo_contrato.pdf_path = pdf_filename
                        db.session.commit()
                        flash("Contrato creado y PDF generado exitosamente.", "success")
                    else:
                        flash("Contrato creado pero falló la generación del PDF.", "warning")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    flash(f"Error al crear el contrato: {e}", "danger")
                except Exception as e:
                    flash(f"Error al generar el PDF del contrato: {e}", "danger")
            else:
                flash("Por favor, corrige los errores en el formulario.", "danger")

        return redirect(url_for("lista_contrato"))

    # GET: Listar Contratos
    contratos = Contrato.query.options(joinedload(Contrato.trabajador)).all()

    return render_template(
        'lista_contrato.html',
        contratos=contratos,
        trabajadores=trabajadores,
        form=form,
        empresas_mvs=empresas_mvs,
        clientes=clientes,
        servicios=servicios,
        sucursales=sucursales,
        representantes=representantes
    )

# Ruta para eliminar contratos
@app.route('/contrato/eliminar/<int:id>', methods=['POST'])
def eliminar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    try:
        # Eliminar el archivo PDF asociado si existe
        if contrato.pdf_path:
            pdf_file = os.path.join(app.root_path, 'static', 'pdfs', contrato.pdf_path)
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
                logging.info(f"Archivo PDF {contrato.pdf_path} eliminado.")

        db.session.delete(contrato)
        db.session.commit()
        flash("Contrato eliminado exitosamente.", "success")
        logging.info(f"Contrato con ID {id} eliminado exitosamente.")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al eliminar el contrato: {e}", "danger")
        logging.error(f"Error al eliminar el contrato con ID {id}: {e}")
    except Exception as e:
        flash(f"Error al eliminar el archivo PDF: {e}", "danger")
        logging.error(f"Error al eliminar el archivo PDF para contrato con ID {id}: {e}")

    return redirect(url_for('lista_contrato'))

# Ruta para obtener detalles del contrato en formato JSON (para el modal de edición)
@app.route('/contrato/detalle/<int:id>', methods=['GET'])
def contrato_detalle(id):
    contrato = Contrato.query.get_or_404(id)
    data = {
        'id': contrato.id,
        'trabajador_id': contrato.trabajador_id,
        'fecha_inicio': contrato.fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_termino': contrato.fecha_termino.strftime('%Y-%m-%d') if contrato.fecha_termino else '',
        # Si necesitas más campos, agrégalos aquí
    }
    return jsonify(data)


@app.route('/sucursal', methods=['GET', 'POST'])
def lista_sucursal():
    form = SucursalForm()
    form.cliente_id.choices = [(c.id, c.razon_social) for c in Cliente.query.all()]
    form.region_id.choices = [(r.id, r.region) for r in Region.query.all()]
    form.comuna_id.choices = [(c.id, c.nombre) for c in Comuna.query.all()]
    form.representante_id.choices = [(r.id, f"{r.nombre} {r.apellidop}") for r in Trabajador.query.all()]

    if form.validate_on_submit():
        if form.sucursal_id.data:  # Editar sucursal existente
            sucursal = Sucursal.query.get(form.sucursal_id.data)
            sucursal.cliente_id = form.cliente_id.data
            sucursal.numero_sucursal = form.numero_sucursal.data
            sucursal.nombre_sucursal = form.nombre_sucursal.data
            sucursal.direccion = form.direccion.data
            sucursal.region_id = form.region_id.data
            sucursal.comuna_id = form.comuna_id.data
            sucursal.telefono = form.telefono.data
            sucursal.representante_id = form.representante_id.data
            flash('Sucursal actualizada exitosamente.', 'success')
        else:  # Crear nueva sucursal
            nueva_sucursal = Sucursal(
                cliente_id=form.cliente_id.data,
                numero_sucursal=form.numero_sucursal.data,
                nombre_sucursal=form.nombre_sucursal.data,
                direccion=form.direccion.data,
                region_id=form.region_id.data,
                comuna_id=form.comuna_id.data,
                telefono=form.telefono.data,
                representante_id=form.representante_id.data
            )
            db.session.add(nueva_sucursal)
            flash('Sucursal creada exitosamente.', 'success')

        db.session.commit()
        return redirect(url_for('lista_sucursal'))

    sucursales = Sucursal.query.all()
    return render_template('sucursal/lista_sucursal.html', form=form, sucursales=sucursales)


@app.route('/sucursal/<int:id>', methods=['GET'])
def obtener_sucursal(id):
    sucursal = Sucursal.query.get_or_404(id)
    return jsonify({
        'id': sucursal.id,
        'cliente_id': sucursal.cliente_id,
        'numero_sucursal': sucursal.numero_sucursal,
        'nombre_sucursal': sucursal.nombre_sucursal,
        'direccion': sucursal.direccion,
        'region_id': sucursal.region_id,
        'comuna_id': sucursal.comuna_id,
        'telefono': sucursal.telefono,
        'representante_id': sucursal.representante_id
    })

@app.route('/sucursal/eliminar/<int:id>', methods=['POST'])
def eliminar_sucursal(id):
    sucursal = Sucursal.query.get_or_404(id)
    db.session.delete(sucursal)
    db.session.commit()
    flash('Sucursal eliminada exitosamente.', 'success')
    return redirect(url_for('lista_sucursal'))

def calcular_horas(hora_ingreso, hora_salida_colacion, hora_ingreso_colacion, hora_salida):
    try:
        # Convertir las horas a minutos
        ingreso_min = hora_ingreso.hour * 60 + hora_ingreso.minute
        salida_min = hora_salida.hour * 60 + hora_salida.minute

        # Manejar los casos donde no se definieron las horas de colación
        colacion_salida_min = (hora_salida_colacion.hour * 60 + hora_salida_colacion.minute) if hora_salida_colacion else 0
        colacion_ingreso_min = (hora_ingreso_colacion.hour * 60 + hora_ingreso_colacion.minute) if hora_ingreso_colacion else 0

        # Si las horas de colación no son válidas (por ejemplo, hora_salida_colacion > hora_ingreso_colacion), ignorarlas
        if colacion_salida_min >= colacion_ingreso_min or not hora_salida_colacion or not hora_ingreso_colacion:
            colacion_duracion = 0
        else:
            colacion_duracion = colacion_ingreso_min - colacion_salida_min

        # Calcular las horas trabajadas
        horas_trabajadas = (salida_min - ingreso_min) - colacion_duracion
        return max(0, round(horas_trabajadas / 60, 2))  # Asegurarse de que el resultado no sea negativo
    except Exception as e:
        logger.error(f"Error al calcular horas: {e}")
        return 0


def procesar_dias(dias_form, eliminar_dias_ids):
    lista_dias = []

    for dia_form in dias_form.entries:
        dia_id = dia_form.dia_id.data
        if dia_id and str(dia_id) in eliminar_dias_ids:
            continue

        numero_dia = dia_form.numero_dia.data
        habilitado = dia_form.habilitado.data
        hora_ingreso = dia_form.hora_ingreso.data
        hora_salida_colacion = dia_form.hora_salida_colacion.data
        hora_ingreso_colacion = dia_form.hora_ingreso_colacion.data
        hora_salida = dia_form.hora_salida.data
        turno_gv = dia_form.turno_gv.data

        def hora_a_minutos(hora):
            return hora.hour * 60 + hora.minute if hora else 0

        try:
            ingreso_min = hora_a_minutos(hora_ingreso)
            salida_min = hora_a_minutos(hora_salida)
            colacion_salida_min = hora_a_minutos(hora_salida_colacion)
            colacion_ingreso_min = hora_a_minutos(hora_ingreso_colacion)
            total_minutos = (salida_min - ingreso_min) - ((colacion_ingreso_min - colacion_salida_min)
                if hora_salida_colacion and hora_ingreso_colacion and colacion_ingreso_min > colacion_salida_min else 0)
            total_horas = round(max(total_minutos, 0) / 60, 2)
        except Exception as e:
            app.logger.error(f"Error al calcular horas: {e}")
            total_horas = 0

        nuevo_dia = DiaJornada(
            id=dia_id if dia_id else None,
            numero_dia=numero_dia,
            habilitado=habilitado,
            hora_ingreso=hora_ingreso,
            hora_salida_colacion=hora_salida_colacion,
            hora_ingreso_colacion=hora_ingreso_colacion,
            hora_salida=hora_salida,
            turno_gv=turno_gv,
            total_horas=total_horas
        )
        lista_dias.append(nuevo_dia)

    return lista_dias

@app.route('/jornadas', methods=['GET', 'POST'])
def lista_jornadas():
    form = JornadaForm()

    if form.validate_on_submit():
        app.logger.debug(f"Form data: {request.form}")
        app.logger.debug(f"Form errors: {form.errors}")

        eliminar_dias_ids = request.form.getlist('eliminar_dia')
        jornada_id = form.jornada_id.data
        app.logger.debug(f"Eliminar días: {eliminar_dias_ids}")

        try:
            if jornada_id:  # Editar jornada existente
                jornada = Jornada.query.get_or_404(jornada_id)
                jornada.nombre = form.nombre.data
                jornada.descripcion = form.descripcion.data
                jornada.horas_semanales = float(form.horas_semanales.data) if form.horas_semanales.data else None

                # Eliminar días marcados
                for dia_id in eliminar_dias_ids:
                    DiaJornada.query.filter_by(id=dia_id, jornada_id=jornada.id).delete()

                # Procesar días del formulario
                for i, dia_form in enumerate(form.dias):
                    dia_id = dia_form.dia_id.data
                    app.logger.debug(f"Procesando dia index {i}, id: {dia_id}")

                    numero_dia = dia_form.numero_dia.data
                    habilitado = dia_form.habilitado.data
                    hora_ingreso = dia_form.hora_ingreso.data
                    hora_salida_colacion = dia_form.hora_salida_colacion.data
                    hora_ingreso_colacion = dia_form.hora_ingreso_colacion.data
                    hora_salida = dia_form.hora_salida.data
                    turno_gv = dia_form.turno_gv.data

                    if dia_id:
                        # Día existente: actualizar
                        dia_existente = DiaJornada.query.get(dia_id)
                        if dia_existente:
                            dia_existente.habilitado = habilitado
                            dia_existente.hora_ingreso = hora_ingreso
                            dia_existente.hora_salida_colacion = hora_salida_colacion
                            dia_existente.hora_ingreso_colacion = hora_ingreso_colacion
                            dia_existente.hora_salida = hora_salida
                            dia_existente.turno_gv = turno_gv
                            # Recalcular horas si es necesario
                        else:
                            app.logger.warning(f"Día con ID {dia_id} no encontrado en la BD.")
                    else:
                        # Día nuevo
                        nuevo_dia = DiaJornada(
                            numero_dia=numero_dia,
                            habilitado=habilitado,
                            hora_ingreso=hora_ingreso,
                            hora_salida_colacion=hora_salida_colacion,
                            hora_ingreso_colacion=hora_ingreso_colacion,
                            hora_salida=hora_salida,
                            turno_gv=turno_gv,
                            total_horas=0.0
                        )
                        jornada.dias.append(nuevo_dia)

                db.session.commit()
                flash("Jornada actualizada exitosamente", "success")
            else:
                # Nueva jornada
                nueva_jornada = Jornada(
                    nombre=form.nombre.data,
                    descripcion=form.descripcion.data,
                    horas_semanales=float(form.horas_semanales.data) if form.horas_semanales.data else None
                )

                # Procesar días nuevos
                for i, dia_form in enumerate(form.dias):
                    numero_dia = dia_form.numero_dia.data
                    habilitado = dia_form.habilitado.data
                    hora_ingreso = dia_form.hora_ingreso.data
                    hora_salida_colacion = dia_form.hora_salida_colacion.data
                    hora_ingreso_colacion = dia_form.hora_ingreso_colacion.data
                    hora_salida = dia_form.hora_salida.data
                    turno_gv = dia_form.turno_gv.data

                    nuevo_dia = DiaJornada(
                        numero_dia=numero_dia,
                        habilitado=habilitado,
                        hora_ingreso=hora_ingreso,
                        hora_salida_colacion=hora_salida_colacion,
                        hora_ingreso_colacion=hora_ingreso_colacion,
                        hora_salida=hora_salida,
                        turno_gv=turno_gv,
                        total_horas=0.0
                    )
                    nueva_jornada.dias.append(nuevo_dia)

                db.session.add(nueva_jornada)
                db.session.commit()
                flash("Jornada creada exitosamente", "success")

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error: {e}")
            flash(f"Error al guardar la jornada: {e}", "danger")

        return redirect(url_for('lista_jornadas'))

    jornadas = Jornada.query.options(db.joinedload(Jornada.dias)).all()
    return render_template('jornada/lista_jornadas.html', jornadas=jornadas, form=form)



@app.route('/jornada/detalle/<int:id>', methods=['GET'])
def jornada_detalle(id):
    try:
        jornada = Jornada.query.get_or_404(id)
        data = {
            "id": jornada.id,
            "nombre": jornada.nombre,
            "descripcion": jornada.descripcion or '',
            "dias": [{
                "id": dia.id,
                "numero_dia": dia.numero_dia,
                "habilitado": dia.habilitado,
                "hora_ingreso": dia.hora_ingreso.strftime('%H:%M') if dia.hora_ingreso else '',
                "hora_salida_colacion": dia.hora_salida_colacion.strftime('%H:%M') if dia.hora_salida_colacion else '',
                "hora_ingreso_colacion": dia.hora_ingreso_colacion.strftime('%H:%M') if dia.hora_ingreso_colacion else '',
                "hora_salida": dia.hora_salida.strftime('%H:%M') if dia.hora_salida else '',
                "turno_gv": dia.turno_gv or '',
                "total_horas": dia.total_horas or 0
            } for dia in jornada.dias]
        }
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error al obtener detalle de jornada ID {id}: {e}")
        return jsonify({"error": "Error al obtener los detalles de la jornada"}), 500


@app.route('/jornada/eliminar/<int:id>', methods=['POST'])
def eliminar_jornada(id):
    try:
        jornada = Jornada.query.get_or_404(id)
        db.session.delete(jornada)
        db.session.commit()
        flash("Jornada eliminada exitosamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la jornada: {e}", "danger")
    return redirect(url_for('lista_jornadas'))


@app.route('/jornada/<int:jornada_id>/turnos', methods=['GET'])
def listar_turnos_gv(jornada_id):
    jornada = Jornada.query.get_or_404(jornada_id)
    turnos = TurnoGV.query.filter_by(jornada_id=jornada.id).all()
    return render_template('lista_turnos.html', jornada=jornada, turnos=turnos)


@app.route('/jornada/<int:jornada_id>/turnos/nuevo', methods=['GET', 'POST'])
def agregar_turno_gv(jornada_id):
    jornada = Jornada.query.get_or_404(jornada_id)
    form = TurnoGVForm()
    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        nuevo_turno = TurnoGV(
            jornada_id=jornada.id,
            descripcion=form.descripcion.data,
            hora_ingreso=form.hora_ingreso.data,
            hora_salida=form.hora_salida.data,
            hora_ingreso_colacion=form.hora_ingreso_colacion.data,
            hora_salida_colacion=form.hora_salida_colacion.data
        )
        db.session.add(nuevo_turno)
        db.session.commit()
        flash('Turno GV agregado exitosamente.', 'success')
        return redirect(url_for('listar_turnos_gv', jornada_id=jornada.id))
    return render_template('registro_turno.html', form=form, jornada=jornada)


@app.route('/jornada/<int:jornada_id>/turnos/<int:turno_id>/eliminar', methods=['POST'])
def eliminar_turno_gv(jornada_id, turno_id):
    turno = TurnoGV.query.get_or_404(turno_id)
    db.session.delete(turno)
    db.session.commit()
    flash('Turno GV eliminado exitosamente.', 'success')
    return redirect(url_for('listar_turnos_gv', jornada_id=jornada_id))

@app.route('/clientes', methods=['GET'])
def lista_clientes():
    clientes = Cliente.query.all()
    jornadas = Jornada.query.all()
    sucursales = Sucursal.query.all()
    regiones = Region.query.all()
    comunas = Comuna.query.all()
    return render_template(
        'clientes/lista_clientes.html',
        clientes=clientes,
        jornadas=jornadas,
        sucursales=sucursales,
        regiones=regiones,
        comunas=comunas
    )

@app.route('/clientes/agregar', methods=['POST'])
def agregar_cliente():
    rut = request.form.get('rut')
    razon_social = request.form.get('razon_social')
    region_id = request.form.get('region_id')
    comuna_id = request.form.get('comuna_id')
    direccion = request.form.get('direccion')

    cliente = Cliente(rut=rut, razon_social=razon_social, region_id=region_id, comuna_id=comuna_id, direccion=direccion)
    db.session.add(cliente)
    db.session.commit()
    flash('Cliente agregado exitosamente.', 'success')
    return redirect(url_for('lista_clientes'))

@app.route('/clientes/editar/<int:id>', methods=['POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.rut = request.form.get('rut')
    cliente.razon_social = request.form.get('razon_social')
    cliente.region_id = request.form.get('region_id')
    cliente.comuna_id = request.form.get('comuna_id')
    cliente.direccion = request.form.get('direccion')
    db.session.commit()
    flash('Cliente actualizado exitosamente.', 'success')
    return redirect(url_for('lista_clientes'))

@app.route('/clientes/detalle/<int:id>', methods=['GET'])
def cliente_detalle(id):
    cliente = Cliente.query.get_or_404(id)
    jornadas = Jornada.query.all()
    sucursales = Sucursal.query.filter_by(cliente_id=id).all()
    representantes = Representante.query.filter_by(cliente_id=id).all()
    proyectos = Proyecto.query.filter_by(cliente_id=id).all()  # Agregar proyectos

    cliente_data = {
        "id": cliente.id,
        "rut": cliente.rut,
        "razon_social": cliente.razon_social,
        "region_id": cliente.region_id,
        "comuna_id": cliente.comuna_id,
        "direccion": cliente.direccion,
        "jornadas": [
            {
                "id": jornada.id,
                "nombre": jornada.nombre,
                "descripcion": jornada.descripcion,
                "total_dias": len(jornada.dias)
            }
            for jornada in jornadas
        ],
        "sucursales": [
            {
                "id": sucursal.id,
                "nombre": sucursal.nombre_sucursal,
                "direccion": sucursal.direccion,
                "region": sucursal.region.region,
                "comuna": sucursal.comuna.nombre
            }
            for sucursal in sucursales
        ],
        "representantes": [
            {
                "id": representante.id,
                "nombre": representante.nombre,
                "apellido_paterno": representante.apellido_p,
                "apellido_materno": representante.apellido_m,
                "email": representante.email,
                "telefono": representante.telefono,
                "rol_firma": representante.rol_firma_contratos.nombre
            }
            for representante in representantes
        ],
        "proyectos": [
            {
                "id": proyecto.id,
                "nombre": proyecto.nombre,
                "descripcion": proyecto.descripcion or "Sin descripción",
                "fecha_inicio": proyecto.fecha_inicio.strftime('%Y-%m-%d'),
                "fecha_termino": proyecto.fecha_termino.strftime('%Y-%m-%d') if proyecto.fecha_termino else "No definida"
            }
            for proyecto in proyectos
        ]
    }
    return jsonify(cliente_data), 200




@app.route('/clientes/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el cliente: ' + str(e), 'danger')
    return redirect(url_for('lista_clientes'))

@app.route('/representantes', methods=['GET', 'POST'])
def lista_representantes():
    form = RepresentanteForm()
    # Obtener todos los clientes para llenar las opciones
    clientes = Cliente.query.all()
    roles = RolFirmaContratos.query.all()
    form.cliente_id.choices = [(cliente.id, cliente.razon_social) for cliente in clientes]
    form.rol_firma_contratos_id.choices = [(rol.id, rol.nombre) for rol in roles]

    if form.validate_on_submit():
        representante = Representante(
            cliente_id=form.cliente_id.data,
            nombre=form.nombre.data,
            apellido_p=form.apellido_p.data,
            apellido_m=form.apellido_m.data,
            email=form.email.data,
            telefono=form.telefono.data,
            rol_firma_contratos_id=form.rol_firma_contratos_id.data
        )
        db.session.add(representante)
        db.session.commit()
        flash('Representante agregado exitosamente.', 'success')
        return redirect(url_for('lista_representantes'))

    representantes = Representante.query.all()
    return render_template('representantes/lista_representantes.html', form=form, representantes=representantes, clientes=clientes, roles=roles)

@app.route('/representantes/detalle/<int:representante_id>', methods=['GET'])
def detalle_representante(representante_id):
    representante = Representante.query.get_or_404(representante_id)
    return jsonify({
        'id': representante.id,
        'cliente_id': representante.cliente_id,
        'rol_firma_contratos_id': representante.rol_firma_contratos_id,
        'nombre': representante.nombre,
        'apellido_p': representante.apellido_p,
        'apellido_m': representante.apellido_m,
        'email': representante.email,
        'telefono': representante.telefono
    })

@app.route('/representantes/guardar', methods=['POST'])
def guardar_representante():
    representante_id = request.form.get('representante_id')
    cliente_id = request.form.get('cliente_id')
    rol_firma_contratos_id = request.form.get('rol_firma_contratos_id')
    nombre = request.form.get('nombre')
    apellido_p = request.form.get('apellido_p')
    apellido_m = request.form.get('apellido_m')
    email = request.form.get('email')
    telefono = request.form.get('telefono')

    if representante_id:
        representante = Representante.query.get(representante_id)
        if not representante:
            flash('Representante no encontrado.', 'danger')
            return redirect(url_for('lista_representantes'))
        representante.cliente_id = cliente_id
        representante.rol_firma_contratos_id = rol_firma_contratos_id
        representante.nombre = nombre
        representante.apellido_p = apellido_p
        representante.apellido_m = apellido_m
        representante.email = email
        representante.telefono = telefono
    else:
        representante = Representante(
            cliente_id=cliente_id,
            rol_firma_contratos_id=rol_firma_contratos_id,
            nombre=nombre,
            apellido_p=apellido_p,
            apellido_m=apellido_m,
            email=email,
            telefono=telefono
        )
        db.session.add(representante)

    db.session.commit()
    flash('Representante guardado exitosamente.', 'success')
    return redirect(url_for('lista_representantes'))

@app.route('/representantes/eliminar/<int:id>', methods=['POST'])
def eliminar_representante(id):
    representante = Representante.query.get_or_404(id)
    db.session.delete(representante)
    db.session.commit()
    flash('Representante eliminado exitosamente.', 'success')
    return redirect(url_for('lista_representantes'))

@app.route('/proyectos', methods=['GET'])
def lista_proyectos():
    proyectos = Proyecto.query.all()
    clientes = Cliente.query.all()  # Para el modal de agregar y editar
    return render_template('proyectos/lista_proyectos.html', proyectos=proyectos, clientes=clientes)

@app.route('/proyectos/agregar', methods=['POST'])
def agregar_proyecto():
    form = ProyectoForm()
    if form.validate_on_submit():
        proyecto = Proyecto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_termino=form.fecha_termino.data,
            cliente_id=form.cliente_id.data,
            activo=form.activo.data  # Agregar el campo activo
        )
        db.session.add(proyecto)
        db.session.commit()
        flash('Proyecto agregado exitosamente.', 'success')
    else:
        flash('Error al agregar el proyecto.', 'danger')
    return redirect(url_for('lista_proyectos'))

@app.route('/proyectos/editar/<int:id>', methods=['POST'])
def editar_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id)
    form = ProyectoForm()
    if form.validate_on_submit():
        # Actualización de los campos del proyecto
        proyecto.nombre = form.nombre.data
        proyecto.descripcion = form.descripcion.data
        proyecto.fecha_inicio = form.fecha_inicio.data
        proyecto.fecha_termino = form.fecha_termino.data
        proyecto.cliente_id = form.cliente_id.data
        
        # Nuevo campo: Activo
        proyecto.activo = form.activo.data  # Activo debe estar en tu ProyectoForm como BooleanField

        db.session.commit()
        flash('Proyecto actualizado exitosamente.', 'success')
    else:
        flash('Error al actualizar el proyecto.', 'danger')
    return redirect(url_for('lista_proyectos'))


@app.route('/proyectos/eliminar/<int:id>', methods=['POST'])
def eliminar_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id)
    db.session.delete(proyecto)
    db.session.commit()
    flash('Proyecto eliminado exitosamente.', 'success')
    return redirect(url_for('lista_proyectos'))

@app.route('/proyectos/detalle/<int:id>', methods=['GET'])
def detalle_proyecto(id):
    proyecto = Proyecto.query.get_or_404(id)
    return jsonify({
        'id': proyecto.id,
        'nombre': proyecto.nombre,
        'descripcion': proyecto.descripcion,
        'fecha_inicio': proyecto.fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_termino': proyecto.fecha_termino.strftime('%Y-%m-%d') if proyecto.fecha_termino else '',
        'cliente_id': proyecto.cliente_id,
        'activo': proyecto.activo  # Incluir el campo activo
    })

@app.route('/servicios', methods=['GET', 'POST'])
def lista_servicios():
    form = ServicioForm()
    clientes = Cliente.query.all()
    form.cliente_id.choices = [(cliente.id, cliente.razon_social) for cliente in Cliente.query.all()]

    if form.validate_on_submit():
        servicio = Servicio(
            cliente_id=form.cliente_id.data,
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            fecha_inicio=form.fecha_inicio.data,
            fecha_termino=form.fecha_termino.data,
            activo=form.activo.data
        )
        db.session.add(servicio)
        db.session.commit()
        flash('Servicio agregado exitosamente.', 'success')
        return redirect(url_for('lista_servicios'))
    
    servicios = Servicio.query.all()
    return render_template('servicios/lista_servicios.html', form=form, servicios=servicios, clientes = clientes)

@app.route('/servicios/agregar', methods=['POST'])
def agregar_servicio():
    try:
        servicio_id = request.form.get('servicio_id')
        cliente_id = request.form.get('cliente_id')
        nombre = request.form.get('nombre')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_termino = request.form.get('fecha_termino')

        if servicio_id:  # Si existe un ID, estamos editando
            servicio = Servicio.query.get(servicio_id)
            servicio.cliente_id = cliente_id
            servicio.nombre = nombre
            servicio.fecha_inicio = fecha_inicio
            servicio.fecha_termino = fecha_termino
        else:  # Si no existe un ID, estamos agregando
            nuevo_servicio = Servicio(
                cliente_id=cliente_id,
                nombre=nombre,
                fecha_inicio=fecha_inicio,
                fecha_termino=fecha_termino
            )
            db.session.add(nuevo_servicio)

        db.session.commit()
        flash('Servicio guardado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar el servicio: {e}', 'danger')
    return redirect(url_for('lista_servicios'))

@app.route('/servicios/editar/<int:id>', methods=['POST'])
def editar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    try:
        servicio.cliente_id = request.form.get('cliente_id')
        servicio.nombre = request.form.get('nombre')
        servicio.fecha_inicio = request.form.get('fecha_inicio')
        servicio.fecha_termino = request.form.get('fecha_termino')
        servicio.activo = request.form.get('activo') == 'true'
        db.session.commit()
        flash('Servicio actualizado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el servicio: {e}', 'danger')
    return redirect(url_for('lista_servicios'))


@app.route('/servicios/eliminar/<int:id>', methods=['POST'])
def eliminar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    try:
        db.session.delete(servicio)
        db.session.commit()
        flash('Servicio eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el servicio: {e}', 'danger')
    return redirect(url_for('lista_servicios'))

@app.route('/servicios/<int:id>', methods=['GET'])
def obtener_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    return jsonify({
        'id': servicio.id,
        'cliente_id': servicio.cliente_id,
        'cliente_nombre': servicio.cliente.razon_social,
        'nombre': servicio.nombre,
        'fecha_inicio': servicio.fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_termino': servicio.fecha_termino.strftime('%Y-%m-%d') if servicio.fecha_termino else None,
        'activo': servicio.activo
    })

@app.route('/empresas', methods=['GET', 'POST'])
def lista_empresas():
    form = EmpresaForm()
    empresa_id = request.form.get('empresa_id')

    if form.validate_on_submit():
        if empresa_id:  # Si existe un ID, estamos editando
            empresa = Empresa.query.get(empresa_id)
            if empresa:
                empresa.rut = form.rut.data
                empresa.razon_social = form.razon_social.data
                flash('Empresa actualizada exitosamente.', 'success')
        else:  # Si no existe un ID, estamos agregando
            nueva_empresa = Empresa(
                rut=form.rut.data,
                razon_social=form.razon_social.data
            )
            db.session.add(nueva_empresa)
            flash('Empresa agregada exitosamente.', 'success')

        db.session.commit()
        return redirect(url_for('lista_empresas'))

    empresas = Empresa.query.all()
    return render_template('empresas/lista_empresas.html', form=form, empresas=empresas)


@app.route('/empresas/<int:id>', methods=['GET'])
def obtener_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    return jsonify({
        'id': empresa.id,
        'rut': empresa.rut,
        'razon_social': empresa.razon_social
    })

@app.route('/empresas/agregar', methods=['POST'])
def agregar_empresa():
    try:
        empresa_id = request.form.get('empresa_id')
        rut = request.form.get('rut')
        razon_social = request.form.get('razon_social')

        if empresa_id:  # Si existe un ID, estamos editando
            empresa = Empresa.query.get(empresa_id)
            empresa.rut = rut
            empresa.razon_social = razon_social
        else:  # Si no existe un ID, estamos agregando
            nueva_empresa = Empresa(
                rut=rut,
                razon_social=razon_social
            )
            db.session.add(nueva_empresa)

        db.session.commit()
        flash('Empresa guardada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar la empresa: {e}', 'danger')
    return redirect(url_for('lista_empresas'))


@app.route('/empresas/eliminar/<int:id>', methods=['POST'])
def eliminar_empresa(id):
    try:
        empresa = Empresa.query.get_or_404(id)
        db.session.delete(empresa)
        db.session.commit()
        flash('Empresa eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la empresa: {e}', 'danger')
    return redirect(url_for('lista_empresas'))

@app.route('/plataforma', methods=['GET', 'POST'])
def lista_plataformas():
    form = PlataformaForm()

    if form.validate_on_submit():
        plataforma_id = form.plataforma_id.data
        nombre = form.nombre_plat.data

        try:
            if plataforma_id:
                # Editar plataforma existente
                plataforma = Plataforma.query.get_or_404(plataforma_id)
                plataforma.nombre = nombre
                db.session.commit()
                flash("Plataforma actualizada exitosamente", "success")
            else:
                # Nueva plataforma
                nueva_plataforma = Plataforma(nombre=nombre)
                db.session.add(nueva_plataforma)
                db.session.commit()
                flash("Plataforma creada exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar la plataforma: {e}", "danger")

        return redirect(url_for('lista_plataformas'))

    plataformas = Plataforma.query.all()
    return render_template('plataforma/lista_plataformas.html', plataformas=plataformas, form=form)

@app.route('/plataforma/detalle/<int:id>', methods=['GET'])
def plataforma_detalle(id):
    try:
        plataforma = Plataforma.query.get_or_404(id)
        data = {
            "id": plataforma.id,
            "nombre": plataforma.nombre
        }
        return jsonify(data), 200
    except Exception as e:
        app.logger.error(f"Error al obtener detalle de plataforma ID {id}: {e}")
        return jsonify({"error": "Error al obtener los detalles de la plataforma"}), 500

@app.route('/eliminar_plataforma/<int:id>', methods=['POST'])
def eliminar_plataforma(id):
    try:
        plataforma = Plataforma.query.get_or_404(id)
        db.session.delete(plataforma)
        db.session.commit()
        flash("Plataforma eliminada exitosamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la plataforma: {e}", "danger")

    return redirect(url_for('lista_plataformas'))

@app.route('/causales_contratacion', methods=['GET', 'POST'])
def lista_causales():
    form = CausalContratacionForm()

    if form.validate_on_submit():
        causal_id = form.causal_id.data
        letra = form.letra.data
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        duracion = form.duracion.data

        try:
            if causal_id:
                # Editar causal existente
                causal = CausalContratacion.query.get_or_404(causal_id)
                causal.letra = letra
                causal.nombre = nombre
                causal.descripcion = descripcion
                causal.duracion = duracion
                db.session.commit()
                flash("Causal actualizada exitosamente", "success")
            else:
                # Nueva causal
                nueva_causal = CausalContratacion(
                    letra=letra,
                    nombre=nombre,
                    descripcion=descripcion,
                    duracion=duracion
                )
                db.session.add(nueva_causal)
                db.session.commit()
                flash("Causal creada exitosamente", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar la causal: {e}", "danger")

        return redirect(url_for('lista_causales'))

    causales = CausalContratacion.query.all()
    return render_template('causales/lista_causales.html', causales=causales, form=form)

@app.route('/causales_contratacion/detalle/<int:id>', methods=['GET'])
def causal_contratacion_detalle(id):
    try:
        causal = CausalContratacion.query.get_or_404(id)
        data = {
            "id": causal.id,
            "letra": causal.letra,
            "nombre": causal.nombre,
            "descripcion": causal.descripcion,
            "duracion": causal.duracion
        }
        return jsonify(data), 200
    except Exception as e:
        app.logger.error(f"Error al obtener detalle de causal ID {id}: {e}")
        return jsonify({"error": "Error al obtener los detalles de la causal"}), 500

@app.route('/causales_contratacion/eliminar/<int:id>', methods=['POST'])
def eliminar_causal_contratacion(id):
    try:
        causal = CausalContratacion.query.get_or_404(id)
        db.session.delete(causal)
        db.session.commit()
        flash("Causal eliminada exitosamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la causal: {e}", "danger")

    return redirect(url_for('lista_causales'))

@app.route('/add_afp', methods=['GET', 'POST'])
def add_afp():
    form = AfpForm()
    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_afp = Afp(nombre=form.name.data)
        db.session.add(new_afp)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_afp.html', form=form)

@app.route('/add_banco', methods=['GET', 'POST'])
def add_banco():
    form = BancoForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_banco = Bancos(nombre=form.name.data)
        db.session.add(new_banco)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_banco.html', form=form)

@app.route('/add_comuna', methods=['GET', 'POST'])
def add_comuna():
    form = ComunaForm()
    form.region_id.choices = [(region.id, region.region) for region in Region.query.all()]

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_comuna = Comuna(nombre=form.name.data, region_id=form.region_id.data)
        db.session.add(new_comuna)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_comuna.html', form=form)

@app.route('/add_region', methods=['GET', 'POST'])
def add_region():
    form = RegionForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_region = Region(region=form.name.data)
        db.session.add(new_region)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_region.html', form=form)

@app.route('/add_cuenta', methods=['GET', 'POST'])
def add_cuenta():
    form = CuentaForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_cuenta = Tipo_cuenta(nombre=form.name.data)
        db.session.add(new_cuenta)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_cuenta.html', form=form)

@app.route('/add_pais', methods=['GET', 'POST'])
def add_pais():
    form = PaisForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_pais = Pais(nombre=form.name.data)
        db.session.add(new_pais)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_pais.html', form=form)

@app.route('/add_prevision', methods=['GET', 'POST'])
def add_prevision():
    form = PrevisionForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_prevision = Prev_salud(nombre=form.name.data)
        db.session.add(new_prevision)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_prev.html', form=form)

@app.route('/add_estado_civil', methods=['GET', 'POST'])
def add_estado_civil():
    form = Estado_CivilForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_estado = Estado_Civil(estado=form.name.data)
        db.session.add(new_estado)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_estado_civil.html', form=form)

@app.route('/add_genero', methods=['GET', 'POST'])
def add_genero():
    form = GeneroForm()

    if form.validate_on_submit():
        app.logger.info("Formulario validado correctamente.")
        new_genero = Genero(genero=form.name.data)
        db.session.add(new_genero)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_genero.html', form=form)

if __name__ == '__main__':
    wait_for_db()
    with app.app_context():
        db.create_all()
        print('Tablas creadas en la base de datos.')
    app.run(host='0.0.0.0',port =5000, debug=True)