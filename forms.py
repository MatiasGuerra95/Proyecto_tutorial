from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class WorkerForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired()])
    name = StringField('Nombre', validators=[DataRequired()])
    apellidop = StringField('Apellido Paterno', validators=[DataRequired()])
    apellidom = StringField('Apellido Materno')
    email = StringField('email', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    direccion_calle = StringField('Calle', validators=[DataRequired()])
    direccion_numero = StringField('Número', validators=[DataRequired()])
    direccion_dpto = StringField('Departamento')
    direccion_comuna_id = SelectField('Comuna', coerce=int)
    banco_id = SelectField('Banco', coerce=int, validators=[DataRequired()])
    banco_cuenta_tipo_id = SelectField('Tipo de Cuenta', coerce=int)
    banco_cuenta_numero = StringField('Número de Cuenta', validators=[DataRequired()])
    afp_id = SelectField('AFP', coerce=int, validators=[DataRequired()])
    pais_id = SelectField('País', coerce=int)
    prev_salud_id = SelectField('Previsión de Salud', coerce=int)
    submit = SubmitField('Agregar Trabajador')

class ContractForm(FlaskForm):
    details = StringField('Detalles', validators=[DataRequired()])
    worker_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar Contrato')

class AfpForm(FlaskForm):
    name = StringField('Nombre de la AFP', validators=[DataRequired()])
    submit = SubmitField('Agregar AFP')

class BancoForm(FlaskForm):
    name = StringField('Nombre del Banco', validators=[DataRequired()])
    submit = SubmitField('Agregar Banco')

class ComunaForm(FlaskForm):
    name = StringField('Nombre de la Comuna', validators=[DataRequired()])
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