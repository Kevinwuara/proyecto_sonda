from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class DesplazamientoCOWForm(FlaskForm):
    # ==================== DATOS GENERALES ====================
    responsable = SelectField('Responsable *', choices=[
        ('Sebastian Duarte', 'Sebastian Duarte'),
        ('Juan Pizarro', 'Juan Pizarro'),
        ('Hector Ortiz', 'Hector Ortiz'),
        ('Luis Diaz', 'Luis Diaz')
    ], validators=[DataRequired()])
    
    nombre_sitio = SelectField('Nombre del Sitio *', choices=[], validators=[DataRequired()])
    
    tipo_desplazamiento = SelectField('Desplazamiento *', choices=[
        ('REPLIEGUE', 'REPLIEGUE'),
        ('DESPLIEGUE', 'DESPLIEGUE')
    ], validators=[DataRequired()])
    
    hora_inicio = StringField('Hora Inicio *', validators=[DataRequired(), Length(min=5, max=5)])
    hora_termino = StringField('Hora Término *', validators=[DataRequired(), Length(min=5, max=5)])
    
    # ==================== OBSERVACIONES ====================
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    
    submit = SubmitField('Guardar Inspección')