from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import BancoForm, TrabajadorForm, ContratoForm, DiaContratoForm, AfpForm, ComunaForm, CuentaForm, PaisForm, PrevisionForm, RegionForm, Estado_CivilForm, GeneroForm
from models import Bancos, db, Trabajador, Contrato, DiaContrato, Afp, Comuna, Tipo_cuenta, Pais, Prev_salud, Region, Estado_Civil, Genero
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esto por una clave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Inicializamos db con la aplicación

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

# Rutas de tu aplicación
@app.route('/')
def index():
    trabajador = Trabajador.query.all()
    return render_template('index.html', trabajador=trabajador)

@app.route('/add_trabajador', methods=['GET', 'POST'])
def add_trabajador():
    form = TrabajadorForm()

    form.afp_id.choices = [(afp.id, afp.nombre) for afp in Afp.query.all()]
    form.banco_id.choices = [(banco.id, banco.nombre) for banco in Bancos.query.all()]
    form.comuna_id.choices = [(comuna.id, comuna.nombre) for comuna in Comuna.query.all()]
    form.banco_tipo_cuenta_id.choices = [(banco_tipo_cuenta.id, banco_tipo_cuenta.nombre) for banco_tipo_cuenta in Tipo_cuenta.query.all()]
    form.pais_id.choices = [(pais.id, pais.nombre) for pais in Pais.query.all()]
    form.prev_salud_id.choices = [(prev_salud.id, prev_salud.nombre) for prev_salud in Prev_salud.query.all()]
    form.estado_civil_id.choices = [(estado_civil.id, estado_civil.estado) for estado_civil in Estado_Civil.query.all()]
    form.genero_id.choices = [(genero.id, genero.genero) for genero in Genero.query.all()]

    if form.validate_on_submit():
        new_trabajador = Trabajador(
            rut=form.rut.data,
            nombre=form.nombre.data,
            apellidop=form.apellidop.data,
            apellidom=form.apellidom.data,
            email=form.email.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            comuna_id=form.comuna_id.data,
            direccion_calle=form.direccion_calle.data,
            direccion_numero=form.direccion_numero.data,
            direccion_dpto=form.direccion_dpto.data,
            banco_id=form.banco_id.data,
            banco_tipo_cuenta_id=form.banco_tipo_cuenta_id.data,
            banco_cuenta_numero=form.banco_cuenta_numero.data,
            afp_id=form.afp_id.data,
            pais_id=form.pais_id.data,
            prev_salud_id=form.prev_salud_id.data,
            estado_civil_id=form.estado_civil_id.data,
            genero_id=form.genero_id.data
         )
        pass

        db.session.add(new_trabajador)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_trabajador.html', form=form)

@app.route('/add_contrato', methods=['GET', 'POST'])
def add_contrato():
    form = ContratoForm()
    form.trabajador_id.choices = [(trabajador.id, trabajador.nombre) for trabajador in Trabajador.query.all()]
    if form.validate_on_submit():
        new_contrato = Contrato(trabajador_id=form.trabajador_id.data)
        db.session.add(new_contrato)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_contrato.html', form=form)

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