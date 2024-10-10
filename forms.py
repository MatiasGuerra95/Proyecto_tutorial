from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class WorkerForm(FlaskForm):
    name = StringField('Nombre del Trabajador', validators=[DataRequired()])
    submit = SubmitField('Agregar Trabajador')

class ContractForm(FlaskForm):
    details = StringField('Detalles del Contrato', validators=[DataRequired()])
    worker_id = SelectField('Trabajador', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Agregar Contrato')