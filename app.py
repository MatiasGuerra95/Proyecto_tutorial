from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import WorkerForm, ContractForm, AfpForm
from models import db, Worker, Contract, Afp
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
    if form.validate_on_submit():
        new_worker = Worker(name=form.name.data)
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

if __name__ == '__main__':
    wait_for_db()
    with app.app_context():
        db.create_all()
        print('Tablas creadas en la base de datos.')
    app.run(host='0.0.0.0', debug=True)