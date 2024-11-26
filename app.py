from venv import logger
from flask import Flask, render_template, redirect, url_for, flash, jsonify, send_from_directory, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from forms import BancoForm, TrabajadorForm, ContratoForm, DiaContratoForm, AfpForm, ComunaForm, CuentaForm, PaisForm, PrevisionForm, RegionForm, Estado_CivilForm, GeneroForm, SucursalForm, DiaJornadaForm, JornadaForm, TurnoGVForm, ClienteForm
from models import Bancos, db, Trabajador, Contrato, DiaContrato, Afp, Comuna, Tipo_cuenta, Pais, Prev_salud, Region, Estado_Civil, Genero, FormaPago, Sucursal, Cliente, Jornada, DiaJornada, TurnoGV
from utils import generar_pdf, sanitize_input
from datetime import datetime
import os
import time
import bleach
import logging
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy import func


load_dotenv()

# Configuración básica de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Configurar las variables de entorno
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Función para sanitizar datos en rutas específicas si es necesario
def sanitize_input(data):
    if isinstance(data, str):
        return bleach.clean(data)
    return data
def wait_for_db():
    retries = 5
    while retries > 0:
        try:
            with app.app_context():
                # Intentar conectarse a la base de datos
                db.session.execute('SELECT 1')
            print('¡Conexión exitosa a la base de datos!')
            return
        except OperationalError:
            retries -= 1
            print('Base de datos no disponible, reintentando en 5 segundos...')
            time.sleep(5)
    raise Exception('No se pudo conectar a la base de datos después de varios intentos')


# Manejo de archivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    """Endpoint para servir archivos estáticos."""
    return send_from_directory('static', filename)

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
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
    if request.method == 'POST':
        trabajador_id = request.form.get('trabajador_id')
        trabajador = Trabajador.query.get_or_404(trabajador_id)

        # Actualizar campos del trabajador
        trabajador.nombre = sanitize_input(request.form.get('nombre'))
        trabajador.apellidop = sanitize_input(request.form.get('apellidop'))
        trabajador.apellidom = sanitize_input(request.form.get('apellidom'))
        trabajador.comuna_id = sanitize_input(request.form.get('comuna_id'))

        try:
            db.session.commit()
            flash("Trabajador actualizado exitosamente.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error al actualizar el trabajador: {e}", "danger")

        return redirect(url_for('lista_trabajador'))

    # GET request: Renderizar la lista de trabajadores
    trabajadores = Trabajador.query.all()
    bancos = Bancos.query.all()
    tipos_cuenta = Tipo_cuenta.query.all()
    afps = Afp.query.all()
    previsiones_salud = Prev_salud.query.all()
    return render_template(
        'index.html',
        trabajador=trabajadores,
        bancos=bancos,
        tipos_cuenta=tipos_cuenta,
        afps=afps,
        previsiones_salud=previsiones_salud,
        show_navigation=False
    )


@app.route('/trabajador/crear_trabajador', methods=['GET', 'POST'])
def crear_trabajador():
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

    if form.validate_on_submit():
        form.sanitize_data()
        # Crear un nuevo trabajador con los datos del formulario
        nuevo_trabajador = Trabajador(
            rut=sanitize_input(form.rut.data),
            nombre=sanitize_input(form.nombre.data),
            apellidop=sanitize_input(form.apellidop.data),
            apellidom=sanitize_input(form.apellidom.data),
            email=sanitize_input(form.email.data),
            fecha_nacimiento=sanitize_input(form.fecha_nacimiento.data),
            comuna_id=sanitize_input(form.comuna_id.data),
            direccion_calle=sanitize_input(form.direccion_calle.data),
            direccion_numero=sanitize_input(form.direccion_numero.data),
            direccion_dpto=sanitize_input(form.direccion_dpto.data),
            banco_id=sanitize_input(form.banco_id.data),
            banco_tipo_cuenta_id=sanitize_input(form.banco_tipo_cuenta_id.data),
            banco_cuenta_numero=sanitize_input(form.banco_cuenta_numero.data),
            afp_id=sanitize_input(form.afp_id.data),
            pais_id=sanitize_input(form.pais_id.data),
            prev_salud_id=sanitize_input(form.prev_salud_id.data),
            estado_civil_id=sanitize_input(form.estado_civil_id.data),
            genero_id=sanitize_input(form.genero_id.data)
        )
        try:
            db.session.add(nuevo_trabajador)
            db.session.commit()
            flash("Trabajador creado exitosamente.", "success")
            logger.info("Trabajador creado exitosamente.")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash("Error al crear el trabajador.", "danger")
            logger.error(f"Error al crear el trabajador: {e}")

        return redirect(url_for('lista_trabajador'))

    return render_template('crear_trabajador.html', form=form)



@app.route('/trabajador/detalle/<int:id>', methods=['GET'])
def trabajador_detalle(id):
    trabajador = Trabajador.query.get_or_404(id)
    # Construir un diccionario con los datos del trabajador
    data = {
        "rut": trabajador.rut,
        "nombre": trabajador.nombre,
        "apellidop": trabajador.apellidop,
        "apellidom": trabajador.apellidom,
        "email": trabajador.email,
        "fecha_nacimiento": trabajador.fecha_nacimiento.strftime('%Y-%m-%d') if trabajador.fecha_nacimiento else "",
        "telefono": trabajador.telefono,
        "genero_id": trabajador.genero_id,
        "estado_civil_id": trabajador.estado_civil_id,
        "comuna_id": trabajador.comuna_id,
        "direccion_calle": trabajador.direccion_calle,
        "direccion_numero": trabajador.direccion_numero,
        "direccion_dpto": trabajador.direccion_dpto,
        "banco_id": trabajador.banco_id,
        "banco_tipo_cuenta_id": trabajador.banco_tipo_cuenta_id,
        "banco_cuenta_numero": trabajador.banco_cuenta_numero,
        "afp_id": trabajador.afp_id,
        "pais_id": trabajador.pais_id,
        "prev_salud_id": trabajador.prev_salud_id,
    }
    return jsonify(data)

@app.route('/delete_trabajador/<int:trabajador_id>', methods=['POST'])
def delete_trabajador(trabajador_id):
    trabajador = Trabajador.query.get_or_404(trabajador_id)
    
    # Comprobar si el trabajador tiene contratos
    if trabajador.contratos:  # `contratos` es el nombre de la relación en el modelo
        flash("El trabajador no puede ser eliminado, porque tiene un contrato vigente.", "danger")
        logger.warning(f"Intento de eliminación de trabajador con contratos: ID {trabajador_id}")
        return redirect(url_for('index'))
    
    try:
        db.session.delete(trabajador)
        db.session.commit()
        flash("Trabajador eliminado exitosamente.", "success")
        logger.info(f"Trabajador con ID {trabajador_id} eliminado exitosamente.")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Error al eliminar el trabajador.", "danger")
        logger.error(f"Error al eliminar el trabajador con ID {trabajador_id}: {e}")

    return redirect(url_for('index'))

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
    comunas = [{"id": comuna.id, "nombre": comuna.nombre} for comuna in Comuna.query.all()]
    formas_pago = [{"id": forma.id, "nombre": forma.nombre} for forma in FormaPago.query.all()]

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
        "formas_pago": formas_pago        
    })

@app.route('/contrato', methods=['GET'])
def lista_contrato():
    try:
        contratos = Contrato.query.all()  # Asegúrate de que `Contrato` está definido
        return render_template("lista_contrato.html", contratos=contratos)
    except Exception as e:
        app.logger.error(f"Error al cargar contratos: {e}")
        return render_template("500.html"), 500

@app.route("/contrato/crear", methods=["GET", "POST"])
def crear_contrato():
    form = ContratoForm()
    form.trabajador_id.choices = [
            (trabajador.id, f"{trabajador.nombre} {trabajador.apellidop}")
            for trabajador in Trabajador.query.all()
        ]
    

    if form.validate_on_submit():
        trabajador_id = form.trabajador_id.data
        fecha_inicio = form.fecha_inicio.data
        fecha_termino = form.fecha_termino.data

        trabajador = Trabajador.query.get(trabajador_id)
        if not trabajador:
            flash("El trabajador seleccionado no existe.", "danger")
            logger.error(f"Trabajador con ID {trabajador_id} no encontrado.")
            return redirect(url_for("crear_contrato"))

        nuevo_contrato = Contrato(
            trabajador_id=trabajador_id,
            fecha_inicio=fecha_inicio,
            fecha_termino=fecha_termino,
        )

        pdf_filename = generar_pdf(trabajador, fecha_inicio, fecha_termino)
        if pdf_filename:
            nuevo_contrato.pdf_path = pdf_filename
            try:
                db.session.add(nuevo_contrato)
                db.session.commit()
                flash("Contrato creado exitosamente y PDF generado.", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error al crear el contrato.", "danger")
                logger.error(f"Error al crear el contrato: {e}")
        else:
            flash("Hubo un error al generar el PDF.", "danger")

        return redirect(url_for("lista_contrato"))

    return render_template("crear_contrato.html", form=form)


@app.route('/contrato/editar/<int:id>', methods=['GET', 'POST'])
def editar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    form = ContratoForm(obj=contrato)

    # Poblar opciones del campo trabajador
    form.trabajador_id.choices = [
        (trabajador.id, f"{trabajador.nombre} {trabajador.apellidop}")
        for trabajador in Trabajador.query.all()
    ]

    if form.validate_on_submit():
        # Actualizar los datos del contrato
        contrato.trabajador_id = form.trabajador_id.data
        contrato.fecha_inicio = form.fecha_inicio.data
        contrato.fecha_termino = form.fecha_termino.data

        # Buscar el trabajador actualizado
        trabajador = Trabajador.query.get(contrato.trabajador_id)

        try:
            # Regenerar el PDF
            pdf_filename = generar_pdf(
                trabajador, 
                contrato.fecha_inicio, 
                contrato.fecha_termino
            )

            if pdf_filename:
                contrato.pdf_path = pdf_filename  # Actualizar la ruta del PDF

            db.session.commit()
            flash("Contrato y PDF actualizados correctamente.", "success")
            return redirect(url_for('lista_contrato'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar los cambios: {e}", "danger")

    return render_template('editar_contrato.html', form=form, contrato=contrato)


@app.route('/contrato/eliminar/<int:id>', methods=['POST'])
def eliminar_contrato(id):
    contrato = Contrato.query.get_or_404(id)
    db.session.delete(contrato)
    db.session.commit()
    return redirect(url_for('lista_contrato'))

@app.route('/sucursal', methods=['GET'])
def lista_sucursal():
    sucursales = Sucursal.query.all()
    return render_template('sucursal/lista_sucursal.html', sucursales=sucursales)

@app.route('/sucursal/agregar', methods=['GET', 'POST'])
def crear_sucursal():
    form = SucursalForm()
    form.cliente_id.choices = [(c.id, c.razon_social) for c in Cliente.query.all()]
    form.region_id.choices = [(r.id, r.region) for r in Region.query.all()]
    form.comuna_id.choices = [(c.id, c.nombre) for c in Comuna.query.all()]
    form.representante_id.choices = []  # Lista vacía


    if form.validate_on_submit():
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
        db.session.commit()
        flash('Sucursal creada exitosamente.', 'success')
        return redirect(url_for('lista_sucursal'))

    return render_template('sucursal/agregar_sucursal.html', form=form)

@app.route('/sucursal/editar/<int:id>', methods=['GET', 'POST'])
def editar_sucursal(id):
    sucursal = Sucursal.query.get_or_404(id)
    form = SucursalForm(obj=sucursal)
    form.cliente_id.choices = [(c.id, c.razon_social) for c in Cliente.query.all()]
    form.region_id.choices = [(r.id, r.region) for r in Region.query.all()]
    form.comuna_id.choices = [(c.id, c.nombre) for c in Comuna.query.all()]
    form.representante_id.choices = []  # Lista vacía


    if form.validate_on_submit():
        sucursal.cliente_id = form.cliente_id.data
        sucursal.numero_sucursal = form.numero_sucursal.data
        sucursal.nombre_sucursal = form.nombre_sucursal.data
        sucursal.direccion = form.direccion.data
        sucursal.region_id = form.region_id.data
        sucursal.comuna_id = form.comuna_id.data
        sucursal.telefono = form.telefono.data
        sucursal.representante_id = form.representante_id.data
        db.session.commit()
        flash('Sucursal actualizada exitosamente.', 'success')
        return redirect(url_for('lista_sucursal'))

    return render_template('sucursal/editar_sucursal.html', form=form, sucursal=sucursal)

@app.route('/sucursal/eliminar/<int:id>', methods=['POST'])
def eliminar_sucursal(id):
    sucursal = Sucursal.query.get_or_404(id)
    db.session.delete(sucursal)
    db.session.commit()
    flash('Sucursal eliminada exitosamente.', 'success')
    return redirect(url_for('lista_sucursal'))

@app.route('/jornadas', methods=['GET'])
def lista_jornadas():
    """Mostrar todas las jornadas."""
    jornadas = Jornada.query.options(db.joinedload(Jornada.dias)).all()  # Cargar días asociados
    return render_template('jornada/lista_jornadas.html', jornadas=jornadas)


@app.route('/jornada/agregar', methods=['GET', 'POST'])
def agregar_jornada():
    """Crear una nueva jornada."""
    form = JornadaForm()

    if form.validate_on_submit():
        nueva_jornada = Jornada(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data
        )

        # Agregar los días de la jornada
        for dia_form in form.dias.entries:
            nuevo_dia = DiaJornada(
                numero_dia=dia_form.data['numero_dia'],
                hora_ingreso=dia_form.data['hora_ingreso'],
                hora_salida_colacion=dia_form.data['hora_salida_colacion'],
                hora_ingreso_post_colacion=dia_form.data['hora_ingreso_post_colacion'],
                hora_salida=dia_form.data['hora_salida'],
                turno_gv=dia_form.data['turno_gv'],
                horas=dia_form.data['horas']
            )
            nueva_jornada.dias.append(nuevo_dia)

        try:
            db.session.add(nueva_jornada)
            db.session.commit()
            flash("Jornada creada exitosamente.", "success")
            return redirect(url_for('lista_jornadas'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar la jornada: {e}", "danger")

    return render_template('jornada/agregar_jornada.html', form=form)


@app.route('/jornada/editar/<int:id>', methods=['GET', 'POST'])
def editar_jornada(id):
    """Editar una jornada existente."""
    jornada = Jornada.query.get_or_404(id)
    form = JornadaForm(obj=jornada)

    # Poblar los datos iniciales de los días
    if request.method == 'GET':
        while len(form.dias) < len(jornada.dias):
            form.dias.append_entry()

        for i, dia in enumerate(jornada.dias):
            form.dias[i].numero_dia.data = dia.numero_dia
            form.dias[i].hora_ingreso.data = dia.hora_ingreso
            form.dias[i].hora_salida.data = dia.hora_salida

    if form.validate_on_submit():
        jornada.nombre = form.nombre.data
        jornada.descripcion = form.descripcion.data

        # Actualizar días
        for i, dia_form in enumerate(form.dias.entries):
            if i < len(jornada.dias):
                jornada.dias[i].numero_dia = dia_form.data['numero_dia']
                jornada.dias[i].hora_ingreso = dia_form.data['hora_ingreso']
                jornada.dias[i].hora_salida = dia_form.data['hora_salida']
            else:
                nuevo_dia = DiaJornada(
                    numero_dia=dia_form.data['numero_dia'],
                    hora_ingreso=dia_form.data['hora_ingreso'],
                    hora_salida=dia_form.data['hora_salida']
                )
                jornada.dias.append(nuevo_dia)

        try:
            db.session.commit()
            flash("Jornada actualizada exitosamente.", "success")
            return redirect(url_for('lista_jornadas'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la jornada: {e}", "danger")

    return render_template('jornada/editar_jornada.html', form=form, jornada=jornada)


@app.route('/jornada/eliminar/<int:id>', methods=['POST'])
def eliminar_jornada(id):
    """Eliminar una jornada."""
    jornada = Jornada.query.get_or_404(id)

    try:
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

@app.route('/cliente', methods=['GET'])
def lista_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes/lista_clientes.html', clientes=clientes)

@app.route('/cliente/agregar', methods=['GET', 'POST'])
def agregar_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        nuevo_cliente = Cliente(
            razon_social=form.razon_social.data,
            rut=form.rut.data,
            direccion=form.direccion.data,
            comuna_id=form.comuna.data,
            region_id=form.region.data
        )
        try:
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash('Cliente agregado exitosamente', 'success')
            return redirect(url_for('lista_clientes'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error al agregar el cliente: {e}', 'danger')
    return render_template('clientes/agregar_cliente.html', form=form)

@app.route('/cliente/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    
    # Poblar las opciones de los selectores
    form.region_id.choices = [(region.id, region.region) for region in Region.query.all()]
    form.comuna_id.choices = [(comuna.id, comuna.nombre) for comuna in Comuna.query.filter_by(region_id=cliente.region_id).all()]

    if form.validate_on_submit():
        cliente.razon_social = form.razon_social.data
        cliente.direccion = form.direccion.data
        cliente.region_id = form.region_id.data
        cliente.comuna_id = form.comuna_id.data

        try:
            db.session.commit()
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('lista_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cliente: {e}', 'danger')

    return render_template('clientes/editar_cliente.html', form=form)


@app.route('/cliente/eliminar/<int:id>', methods=['POST'])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado exitosamente.', 'success')
    return redirect(url_for('lista_clientes'))




@app.route('/add_afp', methods=['GET', 'POST'])
def add_afp():
    form = AfpForm()
    if form.validate_on_submit():
        new_afp = Afp(nombre=form.name.data)
        db.session.add(new_afp)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_afp.html', form=form)

@app.route('/add_banco', methods=['GET', 'POST'])
def add_banco():
    form = BancoForm()

    if form.validate_on_submit():
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
        new_comuna = Comuna(nombre=form.name.data, region_id=form.region_id.data)
        db.session.add(new_comuna)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_comuna.html', form=form)

@app.route('/add_region', methods=['GET', 'POST'])
def add_region():
    form = RegionForm()

    if form.validate_on_submit():
        new_region = Region(region=form.name.data)
        db.session.add(new_region)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_region.html', form=form)

@app.route('/add_cuenta', methods=['GET', 'POST'])
def add_cuenta():
    form = CuentaForm()

    if form.validate_on_submit():
        new_cuenta = Tipo_cuenta(nombre=form.name.data)
        db.session.add(new_cuenta)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_cuenta.html', form=form)

@app.route('/add_pais', methods=['GET', 'POST'])
def add_pais():
    form = PaisForm()

    if form.validate_on_submit():
        new_pais = Pais(nombre=form.name.data)
        db.session.add(new_pais)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_pais.html', form=form)

@app.route('/add_prevision', methods=['GET', 'POST'])
def add_prevision():
    form = PrevisionForm()

    if form.validate_on_submit():
        new_prevision = Prev_salud(nombre=form.name.data)
        db.session.add(new_prevision)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_prev.html', form=form)

@app.route('/add_estado_civil', methods=['GET', 'POST'])
def add_estado_civil():
    form = Estado_CivilForm()

    if form.validate_on_submit():
        new_estado = Estado_Civil(estado=form.name.data)
        db.session.add(new_estado)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_estado_civil.html', form=form)

@app.route('/add_genero', methods=['GET', 'POST'])
def add_genero():
    form = GeneroForm()

    if form.validate_on_submit():
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