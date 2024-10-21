from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Trabajador(db.Model):
    __tablename__ = 'trabajadores'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidop = db.Column(db.String(100), nullable=False)
    apellidom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(15), nullable=True)  
    genero = db.Column(db.String(10), nullable=True)  
    estado_civil = db.Column(db.String(50), nullable=True)  
    nacionalidad = db.Column(db.String(50), nullable=True)    
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'), nullable=True)
    comuna = db.relationship('Comuna', backref='trabajadores', lazy=True)
    direccion_calle = db.Column(db.String(100), nullable=True)
    direccion_numero = db.Column(db.String(100), nullable=True)
    direccion_dpto = db.Column(db.String(100), nullable=True)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    banco = db.relationship('Bancos', backref='trabajadores', lazy=True)
    banco_tipo_cuenta_id = db.Column(db.Integer, db.ForeignKey('banco_tipo_cuenta.id'), nullable=True)
    banco_tipo_cuenta = db.relationship('Tipo_cuenta', backref='trabajadores', lazy=True)
    banco_cuenta_numero = db.Column(db.String(100), nullable=True)
    contratos = db.relationship('Contrato', backref='trabajadores', lazy=True)
    afp_id = db.Column(db.Integer, db.ForeignKey('afp.id'), nullable=True)
    afp = db.relationship('Afp', backref='trabajadores', lazy=True)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=True)
    pais = db.relationship('Pais', backref='trabajadores', lazy=True)
    prev_salud_id = db.Column(db.Integer, db.ForeignKey('prev_salud.id'), nullable=True)
    prev_salud = db.relationship('Prev_salud', backref='trabajadores', lazy=True)
    
    def __repr__(self):
        return f'<Trabajador {self.rut}>'

class Contrato(db.Model):
    __tablename__ = 'contratos'
    id = db.Column(db.Integer, primary_key=True)
    detalles = db.Column(db.String(200), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_termino = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Contrato {self.detalles}>'
    
class DiaContrato(db.Model):
    __tablename__ = 'dia_contrato'
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contratos.id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajadores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<DiaContrato {self.fecha} - {self.estado}>'
    
class Afp(db.Model):
    __tablename__ = 'afp'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Afp {self.nombre}>'

class Comuna(db.Model):
    __tablename__ = 'comuna'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    region = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<Comuna {self.nombre} - {self.region}>'
    
class Bancos(db.Model):
    __tablename__ = 'banco'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Bancos {self.nombre}>'

class Tipo_cuenta(db.Model):
    __tablename__ = 'banco_tipo_cuenta'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Tipo_cuenta {self.nombre}>'

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Pais {self.nombre}>'

class Prev_salud(db.Model):
    __tablename__ = 'prev_salud'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Prev_salud {self.nombre}>'
