from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import BancoForm, WorkerForm, ContractForm, AfpForm, ComunaForm, CuentaForm, PaisForm, PrevisionForm
from models import Bancos, db, Worker, Contract, Afp, Comuna, Tipo_cuenta, Pais, Prev_salud
import time
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta'  # Cambia esto por una clave segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@postgres_db:5432/mydb'
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
    workers = Worker.query.all()
    return render_template('index.html', workers=workers)

@app.route('/add_worker', methods=['GET', 'POST'])
def add_worker():
    form = WorkerForm()
    # Poblar afp_id con datos de la tabla Afp
    form.afp_id.choices = [(afp.id, afp.name) for afp in Afp.query.all()]
    form.banco_id.choices = [(banco.id, banco.name) for banco in Bancos.query.all()]
    form.comuna_id.choices = [(comuna.id, comuna.name) for comuna in Comuna.query.all()]
    form.cuenta_id.choices = [(cuenta.id, cuenta.name) for cuenta in Tipo_cuenta.query.all()]
    form.pais_id.choices = [(pais.id, pais.name) for pais in Pais.query.all()]
    form.prevision_id.choices = [(prevision.id, prevision.name) for prevision in Prev_salud.query.all()]

    if form.validate_on_submit():
        new_worker = Worker(
            rut=form.rut.data,
            name=form.name.data,
            direccion_calle=form.direccion_calle.data,
            direccion_numero=form.direccion_numero.data,
            direccion_dpto=form.direccion_dpto.data,
            banco_id=form.banco_id.data,
            banco_cuenta_numero=form.banco_cuenta_numero.data,
            afp_id=form.afp_id.data,
            comuna_id=form.comuna_id.data,
            cuenta_id=form.cuenta_id.data,
            pais_id=form.pais_id.data,
            prevision_id=form.prevision_id.data
        )

        db.session.add(new_worker)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_worker.html', form=form)

@app.route('/add_contract', methods=['GET', 'POST'])
def add_contract():
    form = ContractForm()
    form.worker_id.choices = [(worker.id, worker.name) for worker in Worker.query.all()]
    if form.validate_on_submit():
        new_contract = Contract(details=form.details.data, worker_id=form.worker_id.data)
        db.session.add(new_contract)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_contract.html', form=form)

@app.route('/add_afp', methods=['GET', 'POST'])
def add_afp():
    form = AfpForm()
    if form.validate_on_submit():
        new_afp = Afp(name=form.name.data)
        db.session.add(new_afp)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_afp.html', form=form)

@app.route('/add_banco', methods=['GET', 'POST'])
def add_banco():
    form = BancoForm()

    if form.validate_on_submit():
        new_banco = Bancos(name=form.name.data)
        db.session.add(new_banco)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_banco.html', form=form)

@app.route('/add_comuna', methods=['GET', 'POST'])
def add_comuna():
    form = ComunaForm()

    if form.validate_on_submit():
        new_comuna = Comuna(name=form.name.data)
        db.session.add(new_comuna)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_comuna.html', form=form)

@app.route('/add_cuenta', methods=['GET', 'POST'])
def add_cuenta():
    form = CuentaForm()

    if form.validate_on_submit():
        new_cuenta = Tipo_cuenta(name=form.name.data)
        db.session.add(new_cuenta)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_cuenta.html', form=form)

@app.route('/add_pais', methods=['GET', 'POST'])
def add_pais():
    form = PaisForm()

    if form.validate_on_submit():
        new_pais = Pais(name=form.name.data)
        db.session.add(new_pais)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_pais.html', form=form)

@app.route('/add_prevision', methods=['GET', 'POST'])
def add_prevision():
    form = PrevisionForm()

    if form.validate_on_submit():
        new_prevision = Prev_salud(name=form.name.data)
        db.session.add(new_prevision)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_prev.html', form=form)

if __name__ == '__main__':
    wait_for_db()
    with app.app_context():
        db.create_all()
        print('Tablas creadas en la base de datos.')
    app.run(host='0.0.0.0', debug=True)