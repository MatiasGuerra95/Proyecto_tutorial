from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Worker(db.Model):
    __tablename__ = 'workers'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    apellidop = db.Column(db.String(100), nullable=False)
    apellidom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    direccion_comuna_id = db.Column(db.Integer, db.ForeignKey('direccion_comuna.id'), nullable=True)
    direccion_comuna = db.relationship('Comuna', backref='workers', lazy=True)
    direccion_calle = db.Column(db.String(100), nullable=True)
    direccion_numero = db.Column(db.String(100), nullable=True)
    direccion_dpto = db.Column(db.String(100), nullable=True)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    banco = db.relationship('Bancos', backref='workers', lazy=True)
    banco_cuenta_tipo_id = db.Column(db.Integer, db.ForeignKey('banco_tipo_cuenta.id'), nullable=True)
    banco_cuenta_tipo = db.relationship('Tipo_cuenta', backref='workers', lazy=True)
    banco_cuenta_numero = db.Column(db.String(100), nullable=True)
    contracts = db.relationship('Contract', backref='workers', lazy=True)
    afp_id = db.Column(db.Integer, db.ForeignKey('afp.id'), nullable=True)
    afp = db.relationship('Afp', backref='workers', lazy=True)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=True)
    pais = db.relationship('Pais', backref='workers', lazy=True)
    prev_salud_id = db.Column(db.Integer, db.ForeignKey('prev_salud.id'), nullable=True)
    prev_salud = db.relationship('Prev_salud', backref='workers', lazy=True)
    
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
        return f'<Afp {self.name}>'

class Comuna(db.Model):
    __tablename__ = 'direccion_comuna'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Comuna {self.name}>'
class Bancos(db.Model):
    __tablename__ = 'banco'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Bancos {self.name}>'

class Tipo_cuenta(db.Model):
    __tablename__ = 'banco_tipo_cuenta'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Tipo_cuenta {self.name}>'

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Pais {self.name}>'

class Prev_salud(db.Model):
    __tablename__ = 'prev_salud'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Prev_salud {self.name}>'
