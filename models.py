from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellidoP = db.Column(db.String(100), nullable=False)
    apellidoM = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)

    direccion_comuna = db.relationship('Comuna', backref='worker', lazy=True)
    direccion_calle = db.Column(db.String(100), nullable=True)
    direccion_numero = db.Column(db.String(100), nullable=True)
    direccion_dpto = db.Column(db.String(100), nullable=True)

    banco = db.relationship('Bancos', backref='worker', lazy=True)
    banco_cuenta_tipo = db.relationship('Tipo_cuenta', backref='worker', lazy=True)
    banco_cuenta_numero = db.Column(db.String(100), nullable=True)


    contracts = db.relationship('Contract', backref='worker', lazy=True)
    afp = db.relationship('Afp', backref='worker', lazy=True)
    pais = db.relationship('Pais', backref='worker', lazy=True)
    prev_salud = db.relationship('Prev_salud', backref='worker', lazy=True)
    
    def __repr__(self):
        return f'<Worker {self.rut}>'

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(200), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=False)

    def __repr__(self):
        return f'<Contract {self.details}>'
    
class Afp(db.Model):
    __tablename__ = 'afp'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Afp {self.details}>'

class Comuna(db.Model):
    __tablename__ = 'direccion_comuna'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Comuna {self.details}>'
class Bancos(db.Model):
    __tablename__ = 'banco'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Bancos {self.details}>'

class Tipo_cuenta(db.Model):
    __tablename__ = 'banco_tipo_cuenta'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Tipo_cuenta {self.details}>'

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Pais {self.details}>'

class Prev_salud(db.Model):
    __tablename__ = 'prev_salud'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Prev_salud {self.details}>'
