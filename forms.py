import logging
from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, SelectField, IntegerField, TimeField, TextAreaField, FieldList, FormField, BooleanField, HiddenField, FileField, EmailField
from wtforms.validators import DataRequired, Email, Length, Regexp,InputRequired, Optional, ValidationError
import bleach

from models import Trabajador 

logger = logging.getLogger(__name__)

# Función de limpieza para entradas de texto
def sanitize_input(value):
    return bleach.clean(value, strip=True) if isinstance(value, str) else value


class TrabajadorForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), Length(max=10 , message= "El RUT no debe tener más de 10 caracteres."), Regexp(r'^\d{7,8}-[0-9Kk]{1}$', message="Formato de RUT inválido.")])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100), Regexp(r'^[A-Za-z\s]+$', message="El nombre solo debe contener letras y espacios.")])
    apellidop = StringField('Apellido Paterno', validators=[DataRequired()])
    apellidom = StringField('Apellido Materno')
    email = StringField('email', validators=[DataRequired(), Email(message="Email inválido")])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])  
    genero_id = SelectField('Género', coerce=int, validators=[DataRequired()])  
    estado_civil_id = SelectField('Estado Civil', coerce=int, validators=[DataRequired()])  
    direccion_calle = StringField('Calle', validators=[DataRequired()])
    direccion_numero = StringField('Número', validators=[DataRequired()])
    direccion_dpto = StringField('Departamento')
    region_id = SelectField('Región', coerce=int,choices=[], validators=[DataRequired()])
    comuna_id = SelectField('Comuna', coerce=int,choices=[], validators=[DataRequired()])
    banco_id = SelectField('Banco', coerce=int, validators=[DataRequired()])
    banco_tipo_cuenta_id = SelectField('Tipo de Cuenta', coerce=int, validators=[DataRequired()])
    banco_cuenta_numero = StringField('Número de Cuenta', validators=[DataRequired()])
    afp_id = SelectField('AFP', coerce=int, validators=[DataRequired()])
    pais_id = SelectField('Pais', coerce=int, validators=[DataRequired()])
    prev_salud_id = SelectField('Prevision de Salud', coerce=int, validators=[DataRequired()])
    forma_pago_id = SelectField('Forma de Pago',choices=[], coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar Trabajador')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en TrabajadorForm: {self.errors}")
            return False
        # Sanitización de entradas
        self.rut.data = sanitize_input(self.rut.data)
        self.nombre.data = sanitize_input(self.nombre.data)
        self.apellidop.data = sanitize_input(self.apellidop.data)
        self.apellidom.data = sanitize_input(self.apellidom.data)
        self.email.data = sanitize_input(self.email.data)
        #self.pais.data = sanitize_input(self.pais.data)
        self.direccion_calle.data = sanitize_input(self.direccion_calle.data)
        self.direccion_numero.data = sanitize_input(self.direccion_numero.data)
        self.direccion_dpto.data = sanitize_input(self.direccion_dpto.data)
        self.banco_cuenta_numero.data = sanitize_input(self.banco_cuenta_numero.data)
        logger.info("TrabajadorForm validado exitosamente.")
        return True


class ContratoForm(FlaskForm):
    id = HiddenField('ID')  # Campo oculto para la edición
    trabajador_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', validators=[DataRequired()])
    fecha_termino = DateField('Fecha de Término', validators=[Optional()])
    submit = SubmitField('Guardar Contrato')

    def validate_trabajador_id(self, field):
        trabajador = Trabajador.query.get(field.data)
        if not trabajador:
            raise ValidationError("El trabajador seleccionado no existe.")

    def sanitize_data(self):
        self.trabajador_id.data = sanitize_input(self.trabajador_id.data)
        self.fecha_inicio.data = sanitize_input(str(self.fecha_inicio.data))
        self.fecha_termino.data = sanitize_input(str(self.fecha_termino.data)) if self.fecha_termino.data else None

class DiaContratoForm(FlaskForm):
    contrato_id = SelectField('Contrato', coerce=int, validators=[DataRequired()])
    trabajador_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    estado = StringField('Estado', validators=[DataRequired()])
    submit = SubmitField('Agregar Día de Contrato')    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en DiaContratoForm: {self.errors}")
            return False
        self.estado.data = sanitize_input(self.estado.data)
        logger.info("DiaContratoForm validado exitosamente.")
        return True
    
class ClienteForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), Length(max=12)])
    razon_social = StringField('Razón Social', validators=[DataRequired(), Length(max=100)])
    region_id = SelectField('Región', coerce=int, validators=[DataRequired()])
    comuna_id = SelectField('Comuna', coerce=int, validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Guardar')    
    
class SucursalForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    numero_sucursal = StringField('Número de Sucursal', validators=[DataRequired(), Length(max=10)])
    nombre_sucursal = StringField('Nombre de Sucursal', validators=[DataRequired(), Length(max=100)])
    direccion = StringField('Dirección', validators=[DataRequired(), Length(max=200)])
    region_id = SelectField('Región', coerce=int, validators=[DataRequired()])
    comuna_id = SelectField('Comuna', coerce=int, validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=15)])
    representante_id = SelectField('Representante', coerce=int,choices=[], validators=[Optional()])
    submit = SubmitField('Guardar')

class DiaJornadaForm(FlaskForm):
    numero_dia = IntegerField('Número de Día', validators=[InputRequired()])
    habilitado = BooleanField('Habilitado')
    hora_ingreso = TimeField('Hora Ingreso', validators=[InputRequired()])
    hora_salida_colacion = TimeField('Hora Salida Colación', validators=[Optional()])
    hora_ingreso_colacion = TimeField('Hora Ingreso Colación', validators=[Optional()])
    hora_salida = TimeField('Hora Salida', validators=[InputRequired()])
    turno_gv = StringField('Turno GV', validators=[Optional()])
    total_horas = StringField('Total Horas', validators=[Optional()])


class JornadaForm(FlaskForm):
    jornada_id = HiddenField('Jornada ID')  # Campo oculto para edición
    nombre = StringField('Nombre de la Jornada', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    dias = FieldList(FormField(DiaJornadaForm), min_entries=1, max_entries=7)  # Limitar a 7 días
    submit = SubmitField('Guardar Jornada')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en JornadaForm: {self.errors}")
            return False
        # Sanitizar entradas
        self.nombre.data = sanitize_input(self.nombre.data)
        self.descripcion.data = sanitize_input(self.descripcion.data) if self.descripcion.data else None
        for dia_form in self.dias.entries:
            dia_form.numero_dia.data = sanitize_input(dia_form.numero_dia.data)
            dia_form.turno_gv.data = sanitize_input(dia_form.turno_gv.data) if dia_form.turno_gv.data else None
        logger.info("JornadaForm validado exitosamente.")
        return True

class TurnoGVForm(FlaskForm):
    descripcion = StringField('Descripción', validators=[DataRequired()])
    hora_ingreso = TimeField('Hora de Ingreso', validators=[DataRequired()])
    hora_salida = TimeField('Hora de Salida', validators=[DataRequired()])
    hora_ingreso_colacion = TimeField('Hora de Inicio de Colación', validators=[DataRequired()])
    hora_salida_colacion = TimeField('Hora de Fin de Colación', validators=[DataRequired()])
    submit = SubmitField('Guardar')

class RepresentanteForm(FlaskForm):
    representante_id = IntegerField('ID', validators=[Optional()])  # Campo oculto para edición
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()], choices=[])
    rol_firma_contratos_id = SelectField('Rol Firma Contratos', coerce=int, validators=[DataRequired()], choices=[])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    apellido_p = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=100)])
    apellido_m = StringField('Apellido Materno', validators=[Optional(), Length(max=100)])
    email = EmailField('Email', validators=[Optional(), Email(), Length(max=100)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Guardar Representante')  

class ProyectoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción')
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_termino = DateField('Fecha de Término', format='%Y-%m-%d', validators=[Optional()])
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')
  
class ServicioForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, choices =[],validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    fecha_inicio = DateField('Fecha de Inicio', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_termino = DateField('Fecha de Término', format='%Y-%m-%d', validators=[Optional()])
    activo = BooleanField('¿Activo?')
    submit = SubmitField('Guardar')

class EmpresaForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), Length(max=12)])
    razon_social = StringField('Razón Social', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Guardar Empresa')


class AfpForm(FlaskForm):
    name = StringField('Nombre de la AFP', validators=[DataRequired()])
    submit = SubmitField('Agregar AFP')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en AfpForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("AfpForm validado exitosamente.")
        return True

class BancoForm(FlaskForm):
    name = StringField('Nombre del Banco', validators=[DataRequired()])
    submit = SubmitField('Agregar Banco')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en BancoForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("BancoForm validado exitosamente.")
        return True    

class ComunaForm(FlaskForm):
    name = StringField('Nombre de la Comuna', validators=[DataRequired()])
    region_id = SelectField('Región',coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar Comuna')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en ComunaForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("ComunaForm validado exitosamente.")
        return True    

class RegionForm(FlaskForm):
    name = StringField('Nombre de la Region', validators=[DataRequired()])
    submit = SubmitField('Agregar Comuna')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en RegionForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("RegionForm validado exitosamente.")
        return True    

class Estado_CivilForm(FlaskForm):
    name = StringField('Estado Civil', validators=[DataRequired()])
    submit = SubmitField('Agregar Estado Civil')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en Estado_CivilForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("Estado_CivilForm validado exitosamente.")
        return True    

class GeneroForm(FlaskForm):
    name = StringField('Genero', validators=[DataRequired()])
    submit = SubmitField('Agregar Genero')  
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en GeneroForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("GeneroForm validado exitosamente.")
        return True              

class CuentaForm(FlaskForm):
    name = StringField('Tipo de Cuenta', validators=[DataRequired()])
    submit = SubmitField('Agregar Tipo de Cuenta')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en CuentaForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("CuentaForm validado exitosamente.")
        return True    

class PaisForm(FlaskForm):
    name = StringField('Nombre del Pais', validators=[DataRequired()])
    submit = SubmitField('Agregar Pais')
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en PaisForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("PaisForm validado exitosamente.")
        return True    

class PrevisionForm(FlaskForm):
    name = StringField('Nombre de la Prevision', validators=[DataRequired()])
    submit = SubmitField('Agregar Prevision')    
    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            logger.warning(f"Errores de validación en PrevisionForm: {self.errors}")
            return False
        self.name.data = sanitize_input(self.name.data)
        logger.info("PrevisionForm validado exitosamente.")
        return True    