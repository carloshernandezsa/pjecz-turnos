from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class TurnoForm(FlaskForm):
    #detalles de los campos que se mostraran en el formulario de tipo Flask-WTF
    tipoTurno = SelectField('Tipo de turno',  validators=[DataRequired()], choices=[('1', 'Normal'), ('2', 'Urgente')])
    comentarios = StringField('Comentarios')
    nuevoTurno = SubmitField('Nuevo turno')

