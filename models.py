import logging
from extensions import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Time, ForeignKey
from datetime import datetime


logger = logging.getLogger(__name__)

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
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=True)
    region = db.relationship('Region', back_populates='trabajadores')   
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'), nullable=True)
    comuna = db.relationship('Comuna', back_populates='trabajadores', lazy=True)
    direccion_calle = db.Column(db.String(100), nullable=True)
    direccion_numero = db.Column(db.String(100), nullable=True)
    direccion_dpto = db.Column(db.String(100), nullable=True)
    banco_id = db.Column(db.Integer, db.ForeignKey('banco.id'), nullable=True)
    banco = db.relationship('Bancos', backref='trabajador', lazy=True)
    banco_tipo_cuenta_id = db.Column(db.Integer, db.ForeignKey('banco_tipo_cuenta.id'), nullable=True)
    banco_tipo_cuenta = db.relationship('Tipo_cuenta', backref='trabajador', lazy=True)
    banco_cuenta_numero = db.Column(db.String(100), nullable=True)
    contratos = db.relationship('Contrato', back_populates='trabajador', lazy=True, cascade = "all, delete-orphan")
    afp_id = db.Column(db.Integer, db.ForeignKey('afp.id'), nullable=True)
    afp = db.relationship('Afp', backref='trabajador', lazy=True)
    pais_id = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=True)
    pais = db.relationship('Pais', backref='trabajador', lazy=True)
    prev_salud_id = db.Column(db.Integer, db.ForeignKey('prev_salud.id'), nullable=True)
    prev_salud = db.relationship('Prev_salud', backref='trabajador', lazy=True)
    forma_pago_id = db.Column(db.Integer, db.ForeignKey('forma_pago.id'))
    forma_pago = db.relationship('FormaPago', backref='trabajadores')
    
    def __repr__(self):
        return f'<Trabajador {self.rut}>'
    
    def obtener_trabajador_por_id(id):
        try:
            trabajador = Trabajador.query.get(id)
            if trabajador:
                logger.info(f"Trabajador con ID {id} encontrado: {trabajador}")
            else:
                logger.warning(f"No se encontró un trabajador con ID {id}")
            return trabajador
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener el trabajador con ID {id}: {e}")
            return None
        
    @staticmethod
    def crear_trabajador(data):
        try:
            nuevo_trabajador = Trabajador(**data)
            db.session.add(nuevo_trabajador)
            db.session.commit()
            logger.info(f"Trabajador creado exitosamente: {nuevo_trabajador}")
            return nuevo_trabajador
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear un trabajador: {e}")
            return None        

class Contrato(db.Model):
    __tablename__ = 'contrato'
    id = db.Column(db.Integer, primary_key=True)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=True)
    pdf_path = db.Column(db.String(255), nullable=True)  # Ruta del archivo PDF
    __table_args__ = (
        db.UniqueConstraint('trabajador_id', 'fecha_inicio', name='unique_trabajador_fecha'),
    )
    trabajador = db.relationship('Trabajador', back_populates='contratos')

    def __repr__(self):
        return f'<Contrato ID {self.id}>'
    
    @staticmethod
    def obtener_contrato_por_id(id):
        try:
            contrato = Contrato.query.get(id)
            if contrato:
                logger.info(f"Contrato con ID {id} encontrado: {contrato}")
            else:
                logger.warning(f"No se encontró un contrato con ID {id}")
            return contrato
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener el contrato con ID {id}: {e}")
            return None

    
class DiaContrato(db.Model):
    __tablename__ = 'dia_contrato'
    id = db.Column(db.Integer, primary_key=True)
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<DiaContrato {self.fecha} - {self.estado}>'
    
    @staticmethod
    def obtener_dia_contrato_por_id(id):
        """Obtiene un registro de DiaContrato por su ID, con manejo de errores y logging."""
        try:
            dia_contrato = DiaContrato.query.get(id)
            if dia_contrato:
                logger.info(f"Registro DiaContrato con ID {id} encontrado: {dia_contrato}")
            else:
                logger.warning(f"No se encontró el registro DiaContrato con ID {id}")
            return dia_contrato
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener DiaContrato con ID {id}: {e}")
            return None

    @staticmethod
    def crear_dia_contrato(contrato_id, trabajador_id, fecha, estado):
        """Crea un nuevo registro de DiaContrato con manejo de errores y logging."""
        try:
            nuevo_dia_contrato = DiaContrato(
                contrato_id=contrato_id,
                trabajador_id=trabajador_id,
                fecha=fecha,
                estado=estado
            )
            db.session.add(nuevo_dia_contrato)
            db.session.commit()
            logger.info(f"Registro DiaContrato creado exitosamente: {nuevo_dia_contrato}")
            return nuevo_dia_contrato
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear DiaContrato: {e}")
            return None

    @staticmethod
    def actualizar_estado_dia_contrato(id, nuevo_estado):
        """Actualiza el estado de un registro de DiaContrato, con manejo de errores y logging."""
        try:
            dia_contrato = DiaContrato.query.get(id)
            if dia_contrato:
                dia_contrato.estado = nuevo_estado
                db.session.commit()
                logger.info(f"Estado de DiaContrato con ID {id} actualizado a: {nuevo_estado}")
                return dia_contrato
            else:
                logger.warning(f"No se encontró el registro DiaContrato con ID {id} para actualizar")
                return None
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al actualizar el estado de DiaContrato con ID {id}: {e}")
            return None

    @staticmethod
    def eliminar_dia_contrato(id):
        """Elimina un registro de DiaContrato, con manejo de errores y logging."""
        try:
            dia_contrato = DiaContrato.query.get(id)
            if dia_contrato:
                db.session.delete(dia_contrato)
                db.session.commit()
                logger.info(f"Registro DiaContrato con ID {id} eliminado exitosamente")
                return True
            else:
                logger.warning(f"No se encontró el registro DiaContrato con ID {id} para eliminar")
                return False
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al eliminar el DiaContrato con ID {id}: {e}")
            return False    
        
class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), nullable=False)
    razon_social = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'), nullable=False)
    direccion = db.Column(db.String(200))

    # Relaciones
    region = db.relationship('Region', backref='cliente')  # Relación con la tabla `region`
    comuna = db.relationship('Comuna', backref='cliente')  # Relación con la tabla `comuna`
    sucursales = db.relationship('Sucursal', backref='cliente', cascade='all, delete-orphan')  # Relación con `Sucursal`
    servicios = db.relationship('Servicio', back_populates='cliente', cascade='all, delete-orphan')  # Relación con `Servicio`
    proyectos = db.relationship('Proyecto', back_populates='cliente', cascade='all, delete-orphan')  # Relación con `Proyecto`

    def __repr__(self):
        return f"<Cliente(id={self.id}, rut={self.rut}, razon_social={self.razon_social})>"



class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    numero_sucursal = db.Column(db.String(10), nullable=False)
    nombre_sucursal = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    comuna_id = db.Column(db.Integer, db.ForeignKey('comuna.id'), nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    representante_id = db.Column(db.Integer, db.ForeignKey('trabajador.id'), nullable=True)

    # Relaciones
    region = relationship("Region", backref="sucursales")  # Relación con `region`
    comuna = relationship("Comuna", backref="sucursales")  # Relación con `comuna`
    representante = relationship("Trabajador", backref="sucursales", lazy="joined")  # Relación con `trabajador`

    def __repr__(self):
        return f"<Sucursal(id={self.id}, numero_sucursal={self.numero_sucursal}, nombre_sucursal={self.nombre_sucursal})>"
    
class Jornada(db.Model):
    __tablename__ = 'jornada'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    horas_semanales = db.Column(db.Float, nullable=True)  # Nuevo campo
    
    dias = db.relationship(
        'DiaJornada',
        back_populates='jornada',
        cascade='all, delete-orphan',
        lazy='joined'
    )

    def __repr__(self):
        return f'<Jornada {self.id}: {self.nombre}>'

class DiaJornada(db.Model):
    __tablename__ = 'dia_jornada'

    id = db.Column(db.Integer, primary_key=True)
    numero_dia = db.Column(db.Integer, nullable=False)
    habilitado = db.Column(db.Boolean, default=True)
    hora_ingreso = db.Column(db.Time, nullable=False)
    hora_salida_colacion = db.Column(db.Time, nullable=True)
    hora_ingreso_colacion = db.Column(db.Time, nullable=True)
    hora_salida = db.Column(db.Time, nullable=False)
    turno_gv = db.Column(db.String(50), nullable=True)
    total_horas = db.Column(db.Float, nullable=False, default=0.0)
    jornada_id = db.Column(db.Integer, db.ForeignKey('jornada.id'), nullable=False)
    
    # Relación inversa con Jornada
    jornada = db.relationship('Jornada', back_populates='dias')

    __table_args__ = (
        db.UniqueConstraint('jornada_id', 'numero_dia', name='unique_numero_dia_por_jornada'),
    )    

    def __repr__(self):
        return f'<DiaJornada {self.id}: Día {self.numero_dia} de {self.jornada.nombre}>'

#class TurnoGV(db.Model):
#|    __tablename__ = 'turno_gv'

class RolFirmaContratos(db.Model):
    __tablename__ = 'rol_firma_contratos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<RolFirmaContratos {self.nombre}>'

class Representante(db.Model):
    __tablename__ = 'representantes'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)  # Clave foránea
    rol_firma_contratos_id = db.Column(db.Integer, db.ForeignKey('rol_firma_contratos.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_p = db.Column(db.String(100), nullable=False)
    apellido_m = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)

    # Relaciones
    cliente = db.relationship('Cliente', backref='representantes', lazy=True)
    rol_firma_contratos = db.relationship('RolFirmaContratos', backref='representantes', lazy=True)

    def __repr__(self):
        return f'<Representante {self.nombre} {self.apellido_p}>'
    
class Proyecto(db.Model):
    __tablename__ = 'proyectos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(500))
    fecha_inicio = Column(db.Date, nullable=False)
    fecha_termino = Column(db.Date, nullable=True)
    # Foreign key para referenciar a Cliente
    cliente_id = Column(Integer, ForeignKey('cliente.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    # Relación con Cliente
    cliente = relationship('Cliente', back_populates='proyectos')

    def __repr__(self):
        return f'<Proyecto {self.nombre}'

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    cliente = db.relationship('Cliente', back_populates='servicios')

    def __repr__(self):
        return f'<Servicio {self.nombre}>'

class Empresa(db.Model):
    __tablename__ = 'empresa'

    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(12), nullable=False, unique=True)
    razon_social = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Empresa {self.razon_social}>'

class Plataforma(db.Model):
    __tablename__ = 'plataforma'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Plataforma {self.id}: {self.nombre}>'
    
class CausalContratacion(db.Model):
    __tablename__ = 'causal_contratacion'

    id = db.Column(db.Integer, primary_key=True)
    letra = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    duracion = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<CausalContratacion {self.id}: {self.nombre}>'

    
class Afp(db.Model):
    __tablename__ = 'afp'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Afp {self.nombre}>'
    
    @staticmethod
    def obtener_afp_por_id(id):
        try:
            afp = Afp.query.get(id)
            if afp:
                logger.info(f"AFP con ID {id} encontrado: {afp}")
            else:
                logger.warning(f"No se encontró AFP con ID {id}")
            return afp
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener AFP con ID {id}: {e}")
            return None    

    @staticmethod
    def crear_afp(nombre):
        try:
            nueva_afp = Afp(nombre=nombre)
            db.session.add(nueva_afp)
            db.session.commit()
            logger.info(f"AFP creada exitosamente: {nueva_afp}")
            return nueva_afp
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear AFP: {e}")
            return None        

class Comuna(db.Model):
    __tablename__ = 'comuna'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=True)
    region = db.relationship('Region', back_populates='comunas', lazy=True)
    trabajadores = db.relationship('Trabajador', back_populates='comuna')
    
    def __repr__(self):
        return f'<Comuna {self.nombre} - {self.region}>'
    
    @staticmethod
    def obtener_comuna_por_id(id):
        try:
            comuna = Comuna.query.get(id)
            if comuna:
                logger.info(f"Comuna con ID {id} encontrada: {comuna}")
            else:
                logger.warning(f"No se encontró comuna con ID {id}")
            return comuna
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener comuna con ID {id}: {e}")
            return None

    @staticmethod
    def crear_comuna(nombre, region_id):
        try:
            nueva_comuna = Comuna(nombre=nombre, region_id=region_id)
            db.session.add(nueva_comuna)
            db.session.commit()
            logger.info(f"Comuna creada exitosamente: {nueva_comuna}")
            return nueva_comuna
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear comuna: {e}")
            return None

    
class Region(db.Model):
    __tablename__ = 'region'
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(200), nullable=False)
    comunas = db.relationship('Comuna', back_populates='region')
    trabajadores = db.relationship('Trabajador', back_populates='region', lazy=True)
    
    def __repr__(self):
        return f'<Region {self.region}>'

    @staticmethod
    def obtener_region_por_id(id):
        try:
            region = Region.query.get(id)
            if region:
                logger.info(f"Región con ID {id} encontrada: {region}")
            else:
                logger.warning(f"No se encontró región con ID {id}")
            return region
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener región con ID {id}: {e}")
            return None

    @staticmethod
    def crear_region(region):
        try:
            nueva_region = Region(region=region)
            db.session.add(nueva_region)
            db.session.commit()
            logger.info(f"Región creada exitosamente: {nueva_region}")
            return nueva_region
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear región: {e}")
            return None

class Estado_Civil(db.Model):
    __tablename__ = 'estado_civil'
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Estado_Civil {self.estado}>'
    
    @staticmethod
    def obtener_estado_civil_por_id(id):
        try:
            estado_civil = Estado_Civil.query.get(id)
            if estado_civil:
                logger.info(f"Estado civil con ID {id} encontrado: {estado_civil}")
            else:
                logger.warning(f"No se encontró estado civil con ID {id}")
            return estado_civil
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener estado civil con ID {id}: {e}")
            return None

    @staticmethod
    def crear_estado_civil(estado):
        try:
            nuevo_estado_civil = Estado_Civil(estado=estado)
            db.session.add(nuevo_estado_civil)
            db.session.commit()
            logger.info(f"Estado civil creado exitosamente: {nuevo_estado_civil}")
            return nuevo_estado_civil
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear estado civil: {e}")
            return None


class Genero(db.Model):
    __tablename__ = 'genero'
    id = db.Column(db.Integer, primary_key=True)
    genero = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Genero {self.genero}>' 

    @staticmethod
    def obtener_genero_por_id(id):
        try:
            genero = Genero.query.get(id)
            if genero:
                logger.info(f"Género con ID {id} encontrado: {genero}")
            else:
                logger.warning(f"No se encontró género con ID {id}")
            return genero
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener género con ID {id}: {e}")
            return None

    @staticmethod
    def crear_genero(genero):
        try:
            nuevo_genero = Genero(genero=genero)
            db.session.add(nuevo_genero)
            db.session.commit()
            logger.info(f"Género creado exitosamente: {nuevo_genero}")
            return nuevo_genero
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear género: {e}")
            return None            
    
class Bancos(db.Model):
    __tablename__ = 'banco'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Bancos {self.nombre}>'
    
    @staticmethod
    def obtener_banco_por_id(id):
        try:
            banco = Bancos.query.get(id)
            if banco:
                logger.info(f"Banco con ID {id} encontrado: {banco}")
            else:
                logger.warning(f"No se encontró banco con ID {id}")
            return banco
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener banco con ID {id}: {e}")
            return None

    @staticmethod
    def crear_banco(nombre):
        try:
            nuevo_banco = Bancos(nombre=nombre)
            db.session.add(nuevo_banco)
            db.session.commit()
            logger.info(f"Banco creado exitosamente: {nuevo_banco}")
            return nuevo_banco
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear banco: {e}")
            return None


class Tipo_cuenta(db.Model):
    __tablename__ = 'banco_tipo_cuenta'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)

    @staticmethod
    def obtener_tipo_cuenta_por_id(id):
        try:
            tipo_cuenta = Tipo_cuenta.query.get(id)
            if tipo_cuenta:
                logger.info(f"Tipo de cuenta con ID {id} encontrado: {tipo_cuenta}")
            else:
                logger.warning(f"No se encontró tipo de cuenta con ID {id}")
            return tipo_cuenta
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener tipo de cuenta con ID {id}: {e}")
            return None

    @staticmethod
    def crear_tipo_cuenta(nombre):
        try:
            nuevo_tipo_cuenta = Tipo_cuenta(nombre=nombre)
            db.session.add(nuevo_tipo_cuenta)
            db.session.commit()
            logger.info(f"Tipo de cuenta creado exitosamente: {nuevo_tipo_cuenta}")
            return nuevo_tipo_cuenta
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear tipo de cuenta: {e}")
            return None    
    
    def __repr__(self):
        return f'<Tipo_cuenta {self.nombre}>'

class Pais(db.Model):
    __tablename__ = 'pais'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Pais {self.nombre}>'
    
    @staticmethod
    def obtener_pais_por_id(id):
        try:
            pais = Pais.query.get(id)
            if pais:
                logger.info(f"País con ID {id} encontrado: {pais}")
            else:
                logger.warning(f"No se encontró país con ID {id}")
            return pais
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener país con ID {id}: {e}")
            return None

    @staticmethod
    def crear_pais(nombre):
        try:
            nuevo_pais = Pais(nombre=nombre)
            db.session.add(nuevo_pais)
            db.session.commit()
            logger.info(f"País creado exitosamente: {nuevo_pais}")
            return nuevo_pais
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear país: {e}")
            return None    

class Prev_salud(db.Model):
    __tablename__ = 'prev_salud'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    
    def __repr__(self):
        return f'<Prev_salud {self.nombre}>'
    
    @staticmethod
    def obtener_prev_salud_por_id(id):
        try:
            prev_salud = Prev_salud.query.get(id)
            if prev_salud:
                logger.info(f"Previsión de salud con ID {id} encontrada: {prev_salud}")
            else:
                logger.warning(f"No se encontró previsión de salud con ID {id}")
            return prev_salud
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener previsión de salud con ID {id}: {e}")
            return None

    @staticmethod
    def crear_prev_salud(nombre):
        try:
            nueva_prev_salud = Prev_salud(nombre=nombre)
            db.session.add(nueva_prev_salud)
            db.session.commit()
            logger.info(f"Previsión de salud creada exitosamente: {nueva_prev_salud}")
            return nueva_prev_salud
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error al crear previsión de salud: {e}")
            return None    
        
class FormaPago(db.Model):
    __tablename__ = 'forma_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<FormaPago {self.nombre}>'

    @staticmethod
    def obtener_formas_pago():
        try:
            return FormaPago.query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener las formas de pago: {e}")
            return None
