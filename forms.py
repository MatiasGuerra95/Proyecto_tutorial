from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class TrabajadorForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellidop = StringField('Apellido Paterno', validators=[DataRequired()])
    apellidom = StringField('Apellido Materno')
    email = StringField('email', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])  
    genero = StringField('Género', validators=[DataRequired()])  
    estado_civil = StringField('Estado Civil', validators=[DataRequired()])  
    nacionalidad = StringField('Nacionalidad', validators=[DataRequired()])
    direccion_calle = StringField('Calle', validators=[DataRequired()])
    direccion_numero = StringField('Número', validators=[DataRequired()])
    direccion_dpto = StringField('Departamento')
    comuna_id = SelectField('Comuna', coerce=int, validators=[DataRequired()])
    banco_id = SelectField('Banco', coerce=int, validators=[DataRequired()])
    banco_tipo_cuenta_id = SelectField('Tipo de Cuenta', coerce=int, validators=[DataRequired()])
    banco_cuenta_numero = StringField('Número de Cuenta', validators=[DataRequired()])
    afp_id = SelectField('AFP', coerce=int, validators=[DataRequired()])
    pais_id = SelectField('Pais', coerce=int, validators=[DataRequired()])
    prev_salud_id = SelectField('Prevision de Salud', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar Trabajador')

class ContratoForm(FlaskForm):
    detalles = StringField('Detalles', validators=[DataRequired()])
    trabajador_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de Inicio', validators=[DataRequired()]) 
    fecha_termino = DateField('Fecha de Término', validators=[DataRequired()])
    submit = SubmitField('Agregar Contrato')

class DiaContratoForm(FlaskForm):
    contrato_id = SelectField('Contrato', coerce=int, validators=[DataRequired()])
    trabajador_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    estado = StringField('Estado', validators=[DataRequired()])
    submit = SubmitField('Agregar Día de Contrato')

class AfpForm(FlaskForm):
    name = StringField('Nombre de la AFP', validators=[DataRequired()])
    submit = SubmitField('Agregar AFP')

class BancoForm(FlaskForm):
    name = StringField('Nombre del Banco', validators=[DataRequired()])
    submit = SubmitField('Agregar Banco')

class ComunaForm(FlaskForm):
    name = StringField('Nombre de la Comuna', validators=[DataRequired()])
    region = StringField('Región', validators=[DataRequired()])
    submit = SubmitField('Agregar Comuna')

class CuentaForm(FlaskForm):
    name = StringField('Tipo de Cuenta', validators=[DataRequired()])
    submit = SubmitField('Agregar Tipo de Cuenta')

class PaisForm(FlaskForm):
    name = StringField('Nombre del Pais', validators=[DataRequired()])
    submit = SubmitField('Agregar Pais')

class PrevisionForm(FlaskForm):
    name = StringField('Nombre de la Prevision', validators=[DataRequired()])
    submit = SubmitField('Agregar Prevision')    