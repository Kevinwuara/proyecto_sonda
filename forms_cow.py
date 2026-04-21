from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class InspeccionCOWForm(FlaskForm):
    # ==================== DATOS PRINCIPALES ====================
    responsable = SelectField('Responsable *', choices=[
        ('Sebastian Duarte', 'Sebastian Duarte'),
        ('Juan Pizarro', 'Juan Pizarro'),
        ('Hector Ortiz', 'Hector Ortiz'),
        ('Luis Diaz', 'Luis Diaz')
    ], validators=[DataRequired()])
    
        # Nombre del Sitio - Seleccionable desde base de datos (se llena dinámicamente)
    nombre_sitio = SelectField('Nombre del Sitio *', choices=[], validators=[DataRequired()])
    
    horometro = IntegerField('Horómetro (Valor Alto) *', validators=[DataRequired(), NumberRange(min=0)])
    hora_inicio = StringField('Hora Inicio *', validators=[DataRequired(), Length(min=5, max=5)])
    hora_termino = StringField('Hora Término *', validators=[DataRequired(), Length(min=5, max=5)])
    
    # ==================== GRUPO ELECTRÓGENO CUMMINS Y ESTANQUE DE COMBUSTIBLE ====================
    horas_funcionamiento = IntegerField('Horas de Funcionamiento (Valor Bajo) *', validators=[DataRequired(), NumberRange(min=0)])
    cantidad_arranques = IntegerField('Cantidad de Arranques *', validators=[DataRequired(), NumberRange(min=0)])
    nivel_aceite = SelectField('Nivel de Aceite', choices=[('Minimo', 'Mínimo'), ('Maximo', 'Máximo')], validators=[DataRequired()])
    nivel_combustible = SelectField('Nivel de Combustible', choices=[
        ('E', 'E'),
        ('1/8', '1/8'),
        ('1/4', '1/4'),
        ('3/8', '3/8'),
        ('1/2', '1/2'),
        ('5/8', '5/8'),
        ('3/4', '3/4'),
        ('7/8', '7/8'),
        ('Full', 'Full')
    ], validators=[DataRequired()])
    nivel_refrigerante = SelectField('Nivel de Refrigerante', choices=[('Minimo', 'Mínimo'), ('Maximo', 'Máximo')], validators=[DataRequired()])
    proxima_mantencion = IntegerField('Próxima Mantención *', validators=[DataRequired(), NumberRange(min=0)])
    estado_ge_principal = SelectField('Estado de GE Principal', choices=[('Auto', 'Auto'), ('Shutdown', 'Shutdown')], validators=[DataRequired()])
    uso_ge_auxiliar = SelectField('Uso de GE Auxiliar', choices=[('SI', 'Sí'), ('NO', 'No')], validators=[DataRequired()])
    limpieza_ge_interior = SelectField('Limpieza GE Interior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_radiador = SelectField('Limpieza Radiador', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    sistema_combustible = SelectField('Sistema Combustible', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    arranque_automatico = SelectField('Arranque Automático', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_interior = SelectField('Limpieza Interior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_exterior = SelectField('Limpieza Exterior', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    cable_5p_4p = SelectField('Cable 5p/4p GE Auxiliar', choices=[('SI', 'Sí'), ('NO', 'No')], validators=[DataRequired()])
    adaptador_ge_aux = SelectField('Cuenta con adaptador para GE Aux', choices=[('SI', 'Sí'), ('NO', 'No')], validators=[DataRequired()])
    
    observaciones_ge = TextAreaField('Observaciones', validators=[Optional()])
    
    # ==================== RACK ENERGÍA, TELECOM Y BATERÍAS ====================
    limpieza_rack_energia = SelectField('Limpieza Rack Energía', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_planta_vertiv = SelectField('Estado Planta Vertiv', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    rectificador_n1 = SelectField('Rectificador N°1', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    rectificador_n2 = SelectField('Rectificador N°2', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    rectificador_n3 = SelectField('Rectificador N°3', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_air_scale = SelectField('Estado Air Scale', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_alarmas = SelectField('Estado de Alarmas', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_7250_ixr = SelectField('Estado 7250-IXR', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_fpfh = SelectField('Estado FPFH', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    conversor_solar_n1 = SelectField('Conversor Solar N°1', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    conversor_solar_n2 = SelectField('Conversor Solar N°2', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_rack_baterias = SelectField('Limpieza Rack Baterías', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_baterias = SelectField('Estado Baterías', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_inversor = SelectField('Estado Inversor', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_ventiladores = SelectField('Estado Ventiladores', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    limpieza_rack_telecom = SelectField('Limpieza Rack Telecom', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    
    observaciones_rack = TextAreaField('Observaciones', validators=[Optional()])
    
    # ==================== ESTRUCTURAS, PANELES SOLARES, NEUMÁTICOS ====================
    limpieza_paneles = SelectField('Limpieza de Paneles', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estructura_paneles = SelectField('Estructura de Paneles Solares', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    cantidad_cunas = IntegerField('Cantidad de Cuñas *', validators=[DataRequired(), NumberRange(min=0)])
    checkpoints = SelectField('Checkpoints', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    presion_neumaticos = SelectField('Presión de Neumáticos', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_torre = SelectField('Estado Torre', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    estado_piolas_viento = SelectField('Estado Piolas de Viento', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    nivelacion_carro = SelectField('Nivelación del Carro', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    gatas_posicionamiento = SelectField('Gatas de Posicionamiento', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    manivelas_izaje = SelectField('Manivelas Izaje de Gatas', choices=[('OK', 'OK'), ('NOK', 'NOK')], validators=[DataRequired()])
    
    observaciones_estructuras = TextAreaField('Observaciones', validators=[Optional()])

    # ==================== FOTOGRAFÍAS (3 para observaciones GE) ====================
    foto_1 = StringField('Fotografía 1', validators=[Optional()])
    foto_2 = StringField('Fotografía 2', validators=[Optional()])
    foto_3 = StringField('Fotografía 3', validators=[Optional()])
    
    submit = SubmitField('Guardar Inspección')