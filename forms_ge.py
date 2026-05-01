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

        # ==================== GRUPO ELECTRÓGENO Y ESTANQUE DE COMBUSTIBLE ====================
    cantidad_arranques = IntegerField('Cantidad de Arranques *', validators=[DataRequired(), NumberRange(min=0)])
    horas_funcionamiento = IntegerField('Horas de Funcionamiento *', validators=[DataRequired(), NumberRange(min=0)])
    nivel_aceite = SelectField('Nivel de Aceite', choices=[('Minimo', 'Mínimo'), ('Maximo', 'Máximo')], validators=[DataRequired()])
    nivel_combustible = SelectField('Nivel de Combustible', choices=[
        ('E', 'E'), ('1/8', '1/8'), ('1/4', '1/4'), ('3/8', '3/8'),
        ('1/2', '1/2'), ('5/8', '5/8'), ('3/4', '3/4'), ('7/8', '7/8'), ('Full', 'Full')
    ], validators=[DataRequired()])
    nivel_refrigerante = SelectField('Nivel de Refrigerante', choices=[('Minimo', 'Mínimo'), ('Maximo', 'Máximo')], validators=[DataRequired()])
    proxima_mantencion = IntegerField('Próxima Mantención *', validators=[DataRequired(), NumberRange(min=0)])
    estado_carcasa = SelectField('Estado de Carcasa', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_ge_interior = SelectField('Limpieza GE Interior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_radiador = SelectField('Limpieza Radiador', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    visor_combustible = SelectField('Visor de Combustible', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    arranque_automatico = SelectField('Arranque Automático', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_interior = SelectField('Limpieza Interior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_exterior = SelectField('Limpieza Exterior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    cable_5p_4p = SelectField('Cuenta con Cable 5p/4p', choices=[('SI', 'Sí'), ('NO', 'No')], validators=[DataRequired()])
    
    observaciones = TextAreaField('Observaciones', validators=[Optional()])

        # ==================== FOTOGRAFÍAS (3 para GE Auxiliar) ====================
    foto_1 = StringField('Fotografía 1', validators=[Optional()])
    foto_2 = StringField('Fotografía 2', validators=[Optional()])
    foto_3 = StringField('Fotografía 3', validators=[Optional()])
    
    submit = SubmitField('Guardar Inspección')