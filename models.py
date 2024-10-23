from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Trabajador(db.Model):
    __tablename__ = 'trabajador'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidop = db.Column(db.String(100), nullable=False)
    apellidom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    genero_id = db.Column(db.Integer, db.ForeignKey('genero.id'), nullable=True)  
    genero = db.relationship('Genero', backref='trabajador', lazy=True)
    estado_civil_id = db.Column(db.Integer, db.ForeignKey('estado_civil.id'), nullable=True)  
    estado_civil = db.relationship('Estado_Civil', backref='trabajador', lazy=True)  
    nacionalidad = db.Column(db.String(50), nullable=True)    
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'), nullable=True)
    comuna = db.relationship('Comuna', backref='trabajador', lazy=True)
    direccion_calle = db.Column(db.String(100), nullable=True)
    direccion_numero = db.Column(db.String(100), nullable=True)
    direccion_dpto = db.Column(db.String(100), nullable=True)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    banco = db.relationship('Bancos', backref='trabajador', lazy=True)
    banco_tipo_cuenta_id = db.Column(db.Integer, db.ForeignKey('banco_tipo_cuenta.id'), nullable=True)
    banco_tipo_cuenta = db.relationship('Tipo_cuenta', backref='trabajador', lazy=True)
    banco_cuenta_numero = db.Column(db.String(100), nullable=True)
    contratos = db.relationship('Contrato', backref='trabajador', lazy=True)
    afp_id = db.Column(db.Integer, db.ForeignKey('afp.id'), nullable=True)
    afp = db.relationship('Afp', backref='trabajador', lazy=True)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=True)
    pais = db.relationship('Pais', backref='trabajador', lazy=True)
    prev_salud_id = db.Column(db.Integer, db.ForeignKey('prev_salud.id'), nullable=True)
    prev_salud = db.relationship('Prev_salud', backref='trabajador', lazy=True)
    
    def __repr__(self):
        return f'<Trabajador {self.rut}>'

class Contrato(db.Model):
    __tablename__ = 'contrato'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_termino = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f'<Contrato ID {self.id}>'
    
class DiaContrato(db.Model):
    __tablename__ = 'dia_contrato'
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
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
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=True)
    region = db.relationship('Region', backref='comuna', lazy=True)
    
    def __repr__(self):
        return f'<Comuna {self.nombre} - {self.region}>'
    
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Region {self.region}>'

class Estado_Civil(db.Model):
    __tablename__ = 'estado_civil'
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Estado_Civil {self.estado}>'

class Genero(db.Model):
    __tablename__ = 'genero'
    id = db.Column(db.Integer, primary_key=True)
    genero = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Comuna {self.genero}>'            
    
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
