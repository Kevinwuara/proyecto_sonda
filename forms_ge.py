from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class InspeccionGEForm(FlaskForm):
    # ==================== DATOS GENERALES ====================
    responsable = SelectField('Responsable *', choices=[
        ('Sebastian Duarte', 'Sebastian Duarte'),
        ('Juan Pizarro', 'Juan Pizarro'),
        ('Hector Ortiz', 'Hector Ortiz'),
        ('Luis Diaz', 'Luis Diaz')
    ], validators=[DataRequired()])
    
    nombre_ge = SelectField('Nombre de GE Auxiliar *', choices=[
        ('TICA', 'TICA'),
        ('NOKIA (verde)', 'NOKIA (verde)')
    ], validators=[DataRequired()])
    
    tipo_ge = SelectField('Tipo de GE Auxiliar/Marca-Modelo *', choices=[
        ('FG Wilson P22-6', 'FG Wilson P22-6'),
        ('Pramac', 'Pramac')
    ], validators=[DataRequired()])
    
    horometro = IntegerField('Horómetro *', validators=[DataRequired(), NumberRange(min=0)])
    
    hora_inicio = StringField('Hora Inicio *', validators=[DataRequired(), Length(min=5, max=5)])
    hora_termino = StringField('Hora Término *', validators=[DataRequired(), Length(min=5, max=5)])
    
    potencia_continua = IntegerField('Potencia Continua', validators=[Optional(), NumberRange(min=0)])
    
    submit = SubmitField('Guardar Inspección')