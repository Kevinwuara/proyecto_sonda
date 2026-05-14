from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class MonitoreoNocheForm(FlaskForm):
    # ==================== DATOS GENERALES ====================
    responsable = SelectField('Responsable *', choices=[
        ('Sebastian Duarte', 'Sebastian Duarte'),
        ('Juan Pizarro', 'Juan Pizarro'),
        ('Hector Ortiz', 'Hector Ortiz'),
        ('Luis Diaz', 'Luis Diaz')
    ], validators=[DataRequired()])
    
    nombre_sitio = SelectField('Nombre del Sitio *', choices=[], validators=[DataRequired()])
    
    hora_inicio = StringField('Hora Inicio *', validators=[DataRequired(), Length(min=5, max=5)])
    hora_termino = StringField('Hora Término *', validators=[DataRequired(), Length(min=5, max=5)])
    
    # ==================== 10 OBSERVACIONES CON SUS FOTOS ====================
    observacion_1 = TextAreaField('Observación 1', validators=[Optional()])
    observacion_2 = TextAreaField('Observación 2', validators=[Optional()])
    observacion_3 = TextAreaField('Observación 3', validators=[Optional()])
    observacion_4 = TextAreaField('Observación 4', validators=[Optional()])
    observacion_5 = TextAreaField('Observación 5', validators=[Optional()])
    observacion_6 = TextAreaField('Observación 6', validators=[Optional()])
    observacion_7 = TextAreaField('Observación 7', validators=[Optional()])
    observacion_8 = TextAreaField('Observación 8', validators=[Optional()])
    observacion_9 = TextAreaField('Observación 9', validators=[Optional()])
    observacion_10 = TextAreaField('Observación 10', validators=[Optional()])
    
    submit = SubmitField('Guardar Monitoreo')