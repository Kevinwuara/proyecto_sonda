from flask import Flask, render_template, redirect, url_for, request, session
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from forms_cow import InspeccionCOWForm
from werkzeug.utils import secure_filename
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from flask import send_file

# 1. PRIMERO crear la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-para-sonda-2026'

# 2. SEGUNDO configurar la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sonda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. TERCERO crear la instancia de db
db = SQLAlchemy(app)

# 4. CUARTO definir el modelo de Usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Modelo de Inspección COW
class InspeccionCOW(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    dia_turno = db.Column(db.Integer, nullable=False)
    responsable = db.Column(db.String(50), nullable=False)
    nombre_sitio = db.Column(db.String(150), nullable=False)
    horometro = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.String(10), nullable=False)
    hora_termino = db.Column(db.String(10), nullable=False)
    
    # Grupo Electrógeno Cummins
    horas_funcionamiento = db.Column(db.Integer, nullable=True)
    cantidad_arranques = db.Column(db.Integer, nullable=True)
    nivel_aceite = db.Column(db.String(10), nullable=True)
    nivel_combustible = db.Column(db.String(10), nullable=True)
    nivel_refrigerante = db.Column(db.String(10), nullable=True)
    proxima_mantencion = db.Column(db.Integer, nullable=True)
    estado_ge_principal = db.Column(db.String(10), nullable=True)
    uso_ge_auxiliar = db.Column(db.String(5), nullable=True)
    limpieza_ge_interior = db.Column(db.String(5), nullable=True)
    limpieza_radiador = db.Column(db.String(5), nullable=True)
    sistema_combustible = db.Column(db.String(5), nullable=True)
    arranque_automatico = db.Column(db.String(5), nullable=True)
    limpieza_interior = db.Column(db.String(5), nullable=True)
    limpieza_exterior = db.Column(db.String(5), nullable=True)
    cable_5p_4p = db.Column(db.String(5), nullable=True)
    adaptador_ge_aux = db.Column(db.String(5), nullable=True)
    
    # Rack Energía, Telecom y Baterías
    limpieza_rack_energia = db.Column(db.String(5), nullable=True)
    estado_planta_vertiv = db.Column(db.String(5), nullable=True)
    rectificador_n1 = db.Column(db.String(5), nullable=True)
    rectificador_n2 = db.Column(db.String(5), nullable=True)
    rectificador_n3 = db.Column(db.String(5), nullable=True)
    estado_air_scale = db.Column(db.String(5), nullable=True)
    estado_alarmas = db.Column(db.String(5), nullable=True)
    estado_7250_ixr = db.Column(db.String(5), nullable=True)
    estado_fpfh = db.Column(db.String(5), nullable=True)
    conversor_solar_n1 = db.Column(db.String(5), nullable=True)
    conversor_solar_n2 = db.Column(db.String(5), nullable=True)
    limpieza_rack_baterias = db.Column(db.String(5), nullable=True)
    estado_baterias = db.Column(db.String(5), nullable=True)
    estado_inversor = db.Column(db.String(5), nullable=True)
    estado_ventiladores = db.Column(db.String(5), nullable=True)
    limpieza_rack_telecom = db.Column(db.String(5), nullable=True)
    
    # Estructuras, Paneles Solares, Neumáticos
    limpieza_paneles = db.Column(db.String(5), nullable=True)
    estructura_paneles = db.Column(db.String(5), nullable=True)
    cantidad_cunas = db.Column(db.String(10), nullable=True)
    checkpoints = db.Column(db.String(5), nullable=True)
    presion_neumaticos = db.Column(db.String(5), nullable=True)
    estado_torre = db.Column(db.String(5), nullable=True)
    estado_piolas_viento = db.Column(db.String(5), nullable=True)
    nivelacion_carro = db.Column(db.String(5), nullable=True)
    gatas_posicionamiento = db.Column(db.String(5), nullable=True)
    manivelas_izaje = db.Column(db.String(5), nullable=True)
    
    # Observaciones
    observaciones_ge = db.Column(db.Text, nullable=True)
    observaciones_rack = db.Column(db.Text, nullable=True)
    observaciones_estructuras = db.Column(db.Text, nullable=True)

    # ==================== FOTOGRAFÍAS ====================
    # Fotos GE
    foto_1 = db.Column(db.String(200), nullable=True)
    foto_2 = db.Column(db.String(200), nullable=True)
    foto_3 = db.Column(db.String(200), nullable=True)
    
    # Fotos Rack Energía
    foto_rack_1 = db.Column(db.String(200), nullable=True)
    foto_rack_2 = db.Column(db.String(200), nullable=True)
    foto_rack_3 = db.Column(db.String(200), nullable=True)
    
    # Fotos Estructuras
    foto_estructuras_1 = db.Column(db.String(200), nullable=True)
    foto_estructuras_2 = db.Column(db.String(200), nullable=True)
    foto_estructuras_3 = db.Column(db.String(200), nullable=True)

    # ==================== LEVANTAMIENTO DE FOTOGRAFÍAS (33 puntos) ====================
    foto_levantamiento_1 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_2 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_3 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_4 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_5 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_6 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_7 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_8 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_9 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_10 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_11 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_12 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_13 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_14 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_15 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_16 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_17 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_18 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_19 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_20 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_21 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_22 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_23 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_24 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_25 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_26 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_27 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_28 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_29 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_30 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_31 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_32 = db.Column(db.String(200), nullable=True)
    foto_levantamiento_33 = db.Column(db.String(200), nullable=True)
    
    # ==================== LEVANTAMIENTO FOTOGRAFÍAS DE MEJORAS ====================
    foto_mejora_1 = db.Column(db.String(200), nullable=True)
    descripcion_mejora_1 = db.Column(db.String(500), nullable=True)
    foto_mejora_2 = db.Column(db.String(200), nullable=True)
    descripcion_mejora_2 = db.Column(db.String(500), nullable=True)
    foto_mejora_3 = db.Column(db.String(200), nullable=True)
    descripcion_mejora_3 = db.Column(db.String(500), nullable=True)
    foto_mejora_4 = db.Column(db.String(200), nullable=True)
    descripcion_mejora_4 = db.Column(db.String(500), nullable=True)

    # Estado y control
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aprobado, rechazado
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    usuario = db.relationship('Usuario', backref='inspecciones_cow')
    
    def __repr__(self):
        return f'<InspeccionCOW {self.id} - {self.nombre_sitio}>'

    def __repr__(self):
        return f'<Usuario {self.username}>'

def calcular_fecha_turno(fecha_ingresada=None):
    # Si se ingresa una fecha (desde el formulario), usarla; si no, usar hoy
    if fecha_ingresada:
        print(f"DEBUG - Función recibió fecha: {fecha_ingresada}")
        hoy = datetime.strptime(fecha_ingresada, '%Y-%m-%d')
    else:
        hoy = datetime.now()
    
    print(f"DEBUG - Fecha usada para cálculo: {hoy.strftime('%Y-%m-%d')}")
    
    fecha_str = hoy.strftime('%d/%m/%Y')
    fecha_iso = hoy.strftime('%Y-%m-%d')
    
    # Fecha base: 01/04/2026
    fecha_base = datetime(2026, 4, 1)
    diferencia = (hoy - fecha_base).days
    print(f"DEBUG - Días desde fecha base: {diferencia}")
    
    # Cada ciclo completo son 14 días
    dia_en_ciclo = diferencia % 14
    print(f"DEBUG - Día en ciclo (0-13): {dia_en_ciclo}")
    
    if dia_en_ciclo < 7:
        turno = "A"
        dia_turno = dia_en_ciclo + 1
        estado = f"Turno A 7x7: Día {dia_turno} de trabajo"
    else:
        turno = "B"
        dia_turno = dia_en_ciclo - 6
        estado = f"Turno B 7x7: Día {dia_turno} de trabajo"
    
    print(f"DEBUG - Resultado: {estado}")
    
    return fecha_str, fecha_iso, dia_turno, turno, estado

@app.route('/calcular_turno', methods=['POST'])
def calcular_turno():
    import json
    data = json.loads(request.data)
    fecha = data.get('fecha')
    
    if fecha:
        _, _, _, _, estado_turno = calcular_fecha_turno(fecha)
        return {'estado_turno': estado_turno}
    
    return {'estado_turno': 'Error'}

# 5. QUINTO rutas de la aplicación
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', usuario=session['nombre'], rol=session['rol'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and check_password_hash(usuario.password, password):
            session['username'] = usuario.username
            if usuario.rol == 'tecnico':          # ← corregido: minúscula
                session['nombre'] = 'Técnico Soporte 1C'
            else:
                session['nombre'] = 'Supervisor de Terreno'
            session['rol'] = usuario.rol
            return redirect(url_for('index'))
        else:
            return render_template('login.html', form=form, error='Usuario o contraseña incorrectos')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('menu.html', usuario=session['nombre'])

@app.route('/inspeccion_cow', methods=['GET', 'POST'])
def inspeccion_cow():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    form = InspeccionCOWForm()

    # Inicializar variables
    fecha_actual = None
    fecha_iso = None
    dia_turno = None
    turno = None
    estado_turno = None
    
    if request.method == 'POST' and form.validate_on_submit():
        fecha_seleccionada = request.form.get('fecha')
        if fecha_seleccionada:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno(fecha_seleccionada)
        else:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
        
        # Procesar fotos
        fotos_guardadas = []
        for i in range(1, 4):
            campo_foto = f'foto_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_guardadas.append(filename)

        # Procesar fotos de Rack Energía/Telecom
        fotos_rack = []
        for i in range(1, 4):
            campo_foto = f'foto_rack_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_rack_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_rack.append(filename)

        # Procesar fotos de Estructuras
        fotos_estructuras = []
        for i in range(1, 4):
            campo_foto = f'foto_estructuras_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_est_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_estructuras.append(filename)

        # Procesar fotos de Levantamiento de Fotografías (33 puntos)
        fotos_levantamiento = []
        for i in range(1, 34):
            campo_foto = f'foto_lev_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_lev_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_levantamiento.append(filename)
                else:
                    fotos_levantamiento.append(None)
            else:
                fotos_levantamiento.append(None)
        
        # Procesar fotos de Mejoras (4 fotos con descripciones)
        fotos_mejora = []
        descripciones_mejora = []
        for i in range(1, 5):
            campo_foto = f'foto_mejora_{i}'
            campo_desc = f'desc_mejora_{i}'
            
            # Descripción
            desc = request.form.get(campo_desc, '')
            descripciones_mejora.append(desc)
            
            # Foto
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_mejora_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_mejora.append(filename)
                else:
                    fotos_mejora.append(None)
            else:
                fotos_mejora.append(None)
        
        # ==================== GUARDAR EN BASE DE DATOS ====================
        usuario_actual = Usuario.query.filter_by(username=session['username']).first()
        
        nueva_inspeccion = InspeccionCOW(
            usuario_id=usuario_actual.id,
            fecha=fecha_actual,
            dia_turno=dia_turno,
            responsable=form.responsable.data,
            nombre_sitio=form.nombre_sitio.data,
            horometro=form.horometro.data,
            hora_inicio=form.hora_inicio.data,
            hora_termino=form.hora_termino.data,
            horas_funcionamiento=form.horas_funcionamiento.data,
            cantidad_arranques=form.cantidad_arranques.data,
            nivel_aceite=form.nivel_aceite.data,
            nivel_combustible=form.nivel_combustible.data,
            nivel_refrigerante=form.nivel_refrigerante.data,
            proxima_mantencion=form.proxima_mantencion.data,
            estado_ge_principal=form.estado_ge_principal.data,
            uso_ge_auxiliar=form.uso_ge_auxiliar.data,
            limpieza_ge_interior=form.limpieza_ge_interior.data,
            limpieza_radiador=form.limpieza_radiador.data,
            sistema_combustible=form.sistema_combustible.data,
            arranque_automatico=form.arranque_automatico.data,
            limpieza_interior=form.limpieza_interior.data,
            limpieza_exterior=form.limpieza_exterior.data,
            cable_5p_4p=form.cable_5p_4p.data,
            adaptador_ge_aux=form.adaptador_ge_aux.data,
            observaciones_ge=form.observaciones_ge.data,
            observaciones_rack=form.observaciones_rack.data,
            observaciones_estructuras=form.observaciones_estructuras.data,
            limpieza_rack_energia=form.limpieza_rack_energia.data,
            estado_planta_vertiv=form.estado_planta_vertiv.data,
            rectificador_n1=form.rectificador_n1.data,
            rectificador_n2=form.rectificador_n2.data,
            rectificador_n3=form.rectificador_n3.data,
            estado_air_scale=form.estado_air_scale.data,
            estado_alarmas=form.estado_alarmas.data,
            estado_7250_ixr=form.estado_7250_ixr.data,
            estado_fpfh=form.estado_fpfh.data,
            conversor_solar_n1=form.conversor_solar_n1.data,
            conversor_solar_n2=form.conversor_solar_n2.data,
            limpieza_rack_baterias=form.limpieza_rack_baterias.data,
            estado_baterias=form.estado_baterias.data,
            estado_inversor=form.estado_inversor.data,
            estado_ventiladores=form.estado_ventiladores.data,
            limpieza_rack_telecom=form.limpieza_rack_telecom.data,
            limpieza_paneles=form.limpieza_paneles.data,
            estructura_paneles=form.estructura_paneles.data,
            cantidad_cunas=form.cantidad_cunas.data,
            checkpoints=form.checkpoints.data,
            presion_neumaticos=form.presion_neumaticos.data,
            estado_torre=form.estado_torre.data,
            estado_piolas_viento=form.estado_piolas_viento.data,
            nivelacion_carro=form.nivelacion_carro.data,
            gatas_posicionamiento=form.gatas_posicionamiento.data,
            manivelas_izaje=form.manivelas_izaje.data,
            foto_1=fotos_guardadas[0] if len(fotos_guardadas) > 0 else None,
            foto_2=fotos_guardadas[1] if len(fotos_guardadas) > 1 else None,
            foto_3=fotos_guardadas[2] if len(fotos_guardadas) > 2 else None,
            foto_rack_1=fotos_rack[0] if len(fotos_rack) > 0 else None,
            foto_rack_2=fotos_rack[1] if len(fotos_rack) > 1 else None,
            foto_rack_3=fotos_rack[2] if len(fotos_rack) > 2 else None,
            foto_estructuras_1=fotos_estructuras[0] if len(fotos_estructuras) > 0 else None,
            foto_estructuras_2=fotos_estructuras[1] if len(fotos_estructuras) > 1 else None,
            foto_estructuras_3=fotos_estructuras[2] if len(fotos_estructuras) > 2 else None,
                        # ==================== FOTOS LEVANTAMIENTO ====================
            foto_levantamiento_1=fotos_levantamiento[0] if len(fotos_levantamiento) > 0 and fotos_levantamiento[0] else None,
            foto_levantamiento_2=fotos_levantamiento[1] if len(fotos_levantamiento) > 1 and fotos_levantamiento[1] else None,
            foto_levantamiento_3=fotos_levantamiento[2] if len(fotos_levantamiento) > 2 and fotos_levantamiento[2] else None,
            foto_levantamiento_4=fotos_levantamiento[3] if len(fotos_levantamiento) > 3 and fotos_levantamiento[3] else None,
            foto_levantamiento_5=fotos_levantamiento[4] if len(fotos_levantamiento) > 4 and fotos_levantamiento[4] else None,
            foto_levantamiento_6=fotos_levantamiento[5] if len(fotos_levantamiento) > 5 and fotos_levantamiento[5] else None,
            foto_levantamiento_7=fotos_levantamiento[6] if len(fotos_levantamiento) > 6 and fotos_levantamiento[6] else None,
            foto_levantamiento_8=fotos_levantamiento[7] if len(fotos_levantamiento) > 7 and fotos_levantamiento[7] else None,
            foto_levantamiento_9=fotos_levantamiento[8] if len(fotos_levantamiento) > 8 and fotos_levantamiento[8] else None,
            foto_levantamiento_10=fotos_levantamiento[9] if len(fotos_levantamiento) > 9 and fotos_levantamiento[9] else None,
            foto_levantamiento_11=fotos_levantamiento[10] if len(fotos_levantamiento) > 10 and fotos_levantamiento[10] else None,
            foto_levantamiento_12=fotos_levantamiento[11] if len(fotos_levantamiento) > 11 and fotos_levantamiento[11] else None,
            foto_levantamiento_13=fotos_levantamiento[12] if len(fotos_levantamiento) > 12 and fotos_levantamiento[12] else None,
            foto_levantamiento_14=fotos_levantamiento[13] if len(fotos_levantamiento) > 13 and fotos_levantamiento[13] else None,
            foto_levantamiento_15=fotos_levantamiento[14] if len(fotos_levantamiento) > 14 and fotos_levantamiento[14] else None,
            foto_levantamiento_16=fotos_levantamiento[15] if len(fotos_levantamiento) > 15 and fotos_levantamiento[15] else None,
            foto_levantamiento_17=fotos_levantamiento[16] if len(fotos_levantamiento) > 16 and fotos_levantamiento[16] else None,
            foto_levantamiento_18=fotos_levantamiento[17] if len(fotos_levantamiento) > 17 and fotos_levantamiento[17] else None,
            foto_levantamiento_19=fotos_levantamiento[18] if len(fotos_levantamiento) > 18 and fotos_levantamiento[18] else None,
            foto_levantamiento_20=fotos_levantamiento[19] if len(fotos_levantamiento) > 19 and fotos_levantamiento[19] else None,
            foto_levantamiento_21=fotos_levantamiento[20] if len(fotos_levantamiento) > 20 and fotos_levantamiento[20] else None,
            foto_levantamiento_22=fotos_levantamiento[21] if len(fotos_levantamiento) > 21 and fotos_levantamiento[21] else None,
            foto_levantamiento_23=fotos_levantamiento[22] if len(fotos_levantamiento) > 22 and fotos_levantamiento[22] else None,
            foto_levantamiento_24=fotos_levantamiento[23] if len(fotos_levantamiento) > 23 and fotos_levantamiento[23] else None,
            foto_levantamiento_25=fotos_levantamiento[24] if len(fotos_levantamiento) > 24 and fotos_levantamiento[24] else None,
            foto_levantamiento_26=fotos_levantamiento[25] if len(fotos_levantamiento) > 25 and fotos_levantamiento[25] else None,
            foto_levantamiento_27=fotos_levantamiento[26] if len(fotos_levantamiento) > 26 and fotos_levantamiento[26] else None,
            foto_levantamiento_28=fotos_levantamiento[27] if len(fotos_levantamiento) > 27 and fotos_levantamiento[27] else None,
            foto_levantamiento_29=fotos_levantamiento[28] if len(fotos_levantamiento) > 28 and fotos_levantamiento[28] else None,
            foto_levantamiento_30=fotos_levantamiento[29] if len(fotos_levantamiento) > 29 and fotos_levantamiento[29] else None,
            foto_levantamiento_31=fotos_levantamiento[30] if len(fotos_levantamiento) > 30 and fotos_levantamiento[30] else None,
            foto_levantamiento_32=fotos_levantamiento[31] if len(fotos_levantamiento) > 31 and fotos_levantamiento[31] else None,
            foto_levantamiento_33=fotos_levantamiento[32] if len(fotos_levantamiento) > 32 and fotos_levantamiento[32] else None,
            
            # ==================== FOTOS MEJORAS ====================
            foto_mejora_1=fotos_mejora[0] if len(fotos_mejora) > 0 and fotos_mejora[0] else None,
            descripcion_mejora_1=descripciones_mejora[0] if len(descripciones_mejora) > 0 else None,
            foto_mejora_2=fotos_mejora[1] if len(fotos_mejora) > 1 and fotos_mejora[1] else None,
            descripcion_mejora_2=descripciones_mejora[1] if len(descripciones_mejora) > 1 else None,
            foto_mejora_3=fotos_mejora[2] if len(fotos_mejora) > 2 and fotos_mejora[2] else None,
            descripcion_mejora_3=descripciones_mejora[2] if len(descripciones_mejora) > 2 else None,
            foto_mejora_4=fotos_mejora[3] if len(fotos_mejora) > 3 and fotos_mejora[3] else None,
            descripcion_mejora_4=descripciones_mejora[3] if len(descripciones_mejora) > 3 else None,

            estado='pendiente'
        )
        
        db.session.add(nueva_inspeccion)
        db.session.commit()
        # ================================================================
        
        print("=" * 50)
        print("NUEVA INSPECCIÓN COW - DATOS COMPLETOS")
        print("=" * 50)
        print(f"DEBUG - Fecha seleccionada: {fecha_seleccionada}")
        print(f"DEBUG - Estado turno calculado: {estado_turno}")
        print(f"Responsable: {form.responsable.data}")
        print(f"Sitio: {form.nombre_sitio.data}")
        print(f"Horómetro: {form.horometro.data}")
        print(f"Hora Inicio: {form.hora_inicio.data} / Término: {form.hora_termino.data}")
        print("-" * 30)
        print("GE CUMMINS:")
        print(f"  Horas Func (Valor Bajo): {form.horas_funcionamiento.data}")
        print(f"  Cantidad Arranques: {form.cantidad_arranques.data}")
        print(f"  Nivel Aceite: {form.nivel_aceite.data}")
        print(f"  Nivel Combustible: {form.nivel_combustible.data}")
        print(f"  Nivel Refrigerante: {form.nivel_refrigerante.data}")
        print(f"  Próxima Mantención: {form.proxima_mantencion.data}")
        print(f"  Estado GE Principal: {form.estado_ge_principal.data}")
        print(f"  Uso GE Auxiliar: {form.uso_ge_auxiliar.data}")
        print(f"  Limpieza GE Interior: {form.limpieza_ge_interior.data}")
        print(f"  Limpieza Radiador: {form.limpieza_radiador.data}")
        print(f"  Sistema Combustible: {form.sistema_combustible.data}")
        print(f"  Arranque Automático: {form.arranque_automatico.data}")
        print(f"  Limpieza Interior: {form.limpieza_interior.data}")
        print(f"  Limpieza Exterior: {form.limpieza_exterior.data}")
        print(f"  Cable 5p/4p: {form.cable_5p_4p.data}")
        print(f"  Adaptador GE Aux: {form.adaptador_ge_aux.data}")
        print("-" * 30)
        print("RACK ENERGÍA:")
        print(f"  Limpieza Rack Energía: {form.limpieza_rack_energia.data}")
        print(f"  Estado Planta Vertiv: {form.estado_planta_vertiv.data}")
        print(f"  Rectificador N1/N2/N3: {form.rectificador_n1.data}/{form.rectificador_n2.data}/{form.rectificador_n3.data}")
        print(f"  Estado Air Scale: {form.estado_air_scale.data}")
        print(f"  Estado Alarmas: {form.estado_alarmas.data}")
        print(f"  Estado 7250-IXR: {form.estado_7250_ixr.data}")
        print(f"  Estado FPFH: {form.estado_fpfh.data}")
        print(f"  Conversor Solar N1/N2: {form.conversor_solar_n1.data}/{form.conversor_solar_n2.data}")
        print(f"  Limpieza Rack Baterías: {form.limpieza_rack_baterias.data}")
        print(f"  Estado Baterías: {form.estado_baterias.data}")
        print(f"  Estado Inversor: {form.estado_inversor.data}")
        print(f"  Estado Ventiladores: {form.estado_ventiladores.data}")
        print(f"  Limpieza Rack Telecom: {form.limpieza_rack_telecom.data}")
        print("-" * 30)
        print("ESTRUCTURAS:")
        print(f"  Limpieza Paneles: {form.limpieza_paneles.data}")
        print(f"  Estructura Paneles: {form.estructura_paneles.data}")
        print(f"  Cantidad Cuñas: {form.cantidad_cunas.data}")
        print(f"  Checkpoints: {form.checkpoints.data}")
        print(f"  Presión Neumáticos: {form.presion_neumaticos.data}")
        print(f"  Estado Torre: {form.estado_torre.data}")
        print(f"  Estado Piolas Viento: {form.estado_piolas_viento.data}")
        print(f"  Nivelación Carro: {form.nivelacion_carro.data}")
        print(f"  Gatas Posicionamiento: {form.gatas_posicionamiento.data}")
        print(f"  Manivelas Izaje: {form.manivelas_izaje.data}")
        print("-" * 30)
        print("FOTOS GUARDADAS:")
        for foto in fotos_guardadas:
            print(f"  - {foto}")
        print("FOTOS RACK GUARDADAS:")
        for foto in fotos_rack:
            print(f"  - {foto}")
        print("FOTOS ESTRUCTURAS GUARDADAS:")
        for foto in fotos_estructuras:
            print(f"  - {foto}")
        print("-" * 30)
        print(f"Observaciones GE: {form.observaciones_ge.data}")
        print(f"Observaciones Rack: {form.observaciones_rack.data}")
        print(f"Observaciones Estructuras: {form.observaciones_estructuras.data}")
        print("=" * 50)
        
        mensaje = f"Inspección COW guardada correctamente (ID: {nueva_inspeccion.id})"
        return render_template('formularios/inspeccion_cow.html', form=form, mensaje=mensaje, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)
    
    # GET request
    fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
    return render_template('formularios/inspeccion_cow.html', form=form, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)

@app.route('/inspeccion_ge')
def inspeccion_ge():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('inspeccion_ge.html', usuario=session['nombre'], rol=session['rol'])

@app.route('/desplazamiento')
def desplazamiento():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('desplazamiento.html', usuario=session['nombre'], rol=session['rol'])

@app.route('/monitoreo')
def monitoreo():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('monitoreo.html', usuario=session['nombre'], rol=session['rol'])

@app.route('/ver_informes')
def ver_informes():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Si es supervisor, ve todos; si es técnico, solo los suyos
    if usuario_actual.rol == 'supervisor':
        inspecciones = InspeccionCOW.query.order_by(InspeccionCOW.fecha_registro.desc()).all()
    else:
        inspecciones = InspeccionCOW.query.filter_by(usuario_id=usuario_actual.id).order_by(InspeccionCOW.fecha_registro.desc()).all()
    
    return render_template('ver_informes.html', usuario=session['nombre'], rol=session['rol'], inspecciones=inspecciones)

@app.route('/ver_informe/<int:id>')
def ver_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Verificar permiso para ver
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para ver este informe", 403
    
    return render_template('ver_informe.html', inspeccion=inspeccion, usuario=session['nombre'], rol=session['rol'])

@app.route('/aprobar_informe/<int:id>')
def aprobar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    if usuario_actual.rol != 'supervisor':
        return "Acceso denegado", 403
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    inspeccion.estado = 'aprobado'
    db.session.commit()
    
    return redirect(url_for('ver_informes'))

@app.route('/rechazar_informe/<int:id>')
def rechazar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    if usuario_actual.rol != 'supervisor':
        return "Acceso denegado", 403
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    inspeccion.estado = 'rechazado'
    db.session.commit()
    
    return redirect(url_for('ver_informes'))

@app.route('/editar_informe/<int:id>', methods=['GET', 'POST'])
def editar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Solo el técnico que creó el informe o supervisor puede editar
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para editar este informe", 403
    
    form = InspeccionCOWForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        # Obtener fecha
        fecha_seleccionada = request.form.get('fecha')
        if fecha_seleccionada:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno(fecha_seleccionada)
        else:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
        
        # Actualizar campos de texto
        inspeccion.fecha = fecha_actual
        inspeccion.dia_turno = dia_turno
        inspeccion.responsable = form.responsable.data
        inspeccion.nombre_sitio = form.nombre_sitio.data
        inspeccion.horometro = form.horometro.data
        inspeccion.hora_inicio = form.hora_inicio.data
        inspeccion.hora_termino = form.hora_termino.data
        inspeccion.horas_funcionamiento = form.horas_funcionamiento.data
        inspeccion.cantidad_arranques = form.cantidad_arranques.data
        inspeccion.nivel_aceite = form.nivel_aceite.data
        inspeccion.nivel_combustible = form.nivel_combustible.data
        inspeccion.nivel_refrigerante = form.nivel_refrigerante.data
        inspeccion.proxima_mantencion = form.proxima_mantencion.data
        inspeccion.estado_ge_principal = form.estado_ge_principal.data
        inspeccion.uso_ge_auxiliar = form.uso_ge_auxiliar.data
        inspeccion.limpieza_ge_interior = form.limpieza_ge_interior.data
        inspeccion.limpieza_radiador = form.limpieza_radiador.data
        inspeccion.sistema_combustible = form.sistema_combustible.data
        inspeccion.arranque_automatico = form.arranque_automatico.data
        inspeccion.limpieza_interior = form.limpieza_interior.data
        inspeccion.limpieza_exterior = form.limpieza_exterior.data
        inspeccion.cable_5p_4p = form.cable_5p_4p.data
        inspeccion.adaptador_ge_aux = form.adaptador_ge_aux.data
        inspeccion.observaciones_ge = form.observaciones_ge.data
        inspeccion.observaciones_rack = form.observaciones_rack.data
        inspeccion.observaciones_estructuras = form.observaciones_estructuras.data
        inspeccion.limpieza_rack_energia = form.limpieza_rack_energia.data
        inspeccion.estado_planta_vertiv = form.estado_planta_vertiv.data
        inspeccion.rectificador_n1 = form.rectificador_n1.data
        inspeccion.rectificador_n2 = form.rectificador_n2.data
        inspeccion.rectificador_n3 = form.rectificador_n3.data
        inspeccion.estado_air_scale = form.estado_air_scale.data
        inspeccion.estado_alarmas = form.estado_alarmas.data
        inspeccion.estado_7250_ixr = form.estado_7250_ixr.data
        inspeccion.estado_fpfh = form.estado_fpfh.data
        inspeccion.conversor_solar_n1 = form.conversor_solar_n1.data
        inspeccion.conversor_solar_n2 = form.conversor_solar_n2.data
        inspeccion.limpieza_rack_baterias = form.limpieza_rack_baterias.data
        inspeccion.estado_baterias = form.estado_baterias.data
        inspeccion.estado_inversor = form.estado_inversor.data
        inspeccion.estado_ventiladores = form.estado_ventiladores.data
        inspeccion.limpieza_rack_telecom = form.limpieza_rack_telecom.data
        inspeccion.limpieza_paneles = form.limpieza_paneles.data
        inspeccion.estructura_paneles = form.estructura_paneles.data
        inspeccion.cantidad_cunas = form.cantidad_cunas.data
        inspeccion.checkpoints = form.checkpoints.data
        inspeccion.presion_neumaticos = form.presion_neumaticos.data
        inspeccion.estado_torre = form.estado_torre.data
        inspeccion.estado_piolas_viento = form.estado_piolas_viento.data
        inspeccion.nivelacion_carro = form.nivelacion_carro.data
        inspeccion.gatas_posicionamiento = form.gatas_posicionamiento.data
        inspeccion.manivelas_izaje = form.manivelas_izaje.data
        
        # ==================== PROCESAR FOTOS (mantener existentes o reemplazar) ====================
        # Fotos GE (3)
        for i in range(1, 4):
            campo_foto = f'foto_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    setattr(inspeccion, f'foto_{i}', filename)
        
        # Fotos Rack (3)
        for i in range(1, 4):
            campo_foto = f'foto_rack_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_rack_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    setattr(inspeccion, f'foto_rack_{i}', filename)
        
        # Fotos Estructuras (3)
        for i in range(1, 4):
            campo_foto = f'foto_estructuras_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_est_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    setattr(inspeccion, f'foto_estructuras_{i}', filename)
        
        # Fotos Levantamiento (33)
        for i in range(1, 34):
            campo_foto = f'foto_lev_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_lev_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    setattr(inspeccion, f'foto_levantamiento_{i}', filename)
        
        # Fotos Mejoras (4) y descripciones
        for i in range(1, 5):
            campo_foto = f'foto_mejora_{i}'
            campo_desc = f'desc_mejora_{i}'
            
            # Actualizar descripción
            desc = request.form.get(campo_desc, '')
            setattr(inspeccion, f'descripcion_mejora_{i}', desc)
            
            # Actualizar foto si se subió una nueva
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_mejora_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    setattr(inspeccion, f'foto_mejora_{i}', filename)
        
        # Cambiar estado a pendiente después de editar
        inspeccion.estado = 'pendiente'
        db.session.commit()
        
        return redirect(url_for('ver_informes'))
    
    # GET request - Cargar datos existentes en el formulario
    if request.method == 'GET':
        form.responsable.data = inspeccion.responsable
        form.nombre_sitio.data = inspeccion.nombre_sitio
        form.horometro.data = inspeccion.horometro
        form.hora_inicio.data = inspeccion.hora_inicio
        form.hora_termino.data = inspeccion.hora_termino
        form.horas_funcionamiento.data = inspeccion.horas_funcionamiento
        form.cantidad_arranques.data = inspeccion.cantidad_arranques
        form.nivel_aceite.data = inspeccion.nivel_aceite
        form.nivel_combustible.data = inspeccion.nivel_combustible
        form.nivel_refrigerante.data = inspeccion.nivel_refrigerante
        form.proxima_mantencion.data = inspeccion.proxima_mantencion
        form.estado_ge_principal.data = inspeccion.estado_ge_principal
        form.uso_ge_auxiliar.data = inspeccion.uso_ge_auxiliar
        form.limpieza_ge_interior.data = inspeccion.limpieza_ge_interior
        form.limpieza_radiador.data = inspeccion.limpieza_radiador
        form.sistema_combustible.data = inspeccion.sistema_combustible
        form.arranque_automatico.data = inspeccion.arranque_automatico
        form.limpieza_interior.data = inspeccion.limpieza_interior
        form.limpieza_exterior.data = inspeccion.limpieza_exterior
        form.cable_5p_4p.data = inspeccion.cable_5p_4p
        form.adaptador_ge_aux.data = inspeccion.adaptador_ge_aux
        form.observaciones_ge.data = inspeccion.observaciones_ge
        form.observaciones_rack.data = inspeccion.observaciones_rack
        form.observaciones_estructuras.data = inspeccion.observaciones_estructuras
        form.limpieza_rack_energia.data = inspeccion.limpieza_rack_energia
        form.estado_planta_vertiv.data = inspeccion.estado_planta_vertiv
        form.rectificador_n1.data = inspeccion.rectificador_n1
        form.rectificador_n2.data = inspeccion.rectificador_n2
        form.rectificador_n3.data = inspeccion.rectificador_n3
        form.estado_air_scale.data = inspeccion.estado_air_scale
        form.estado_alarmas.data = inspeccion.estado_alarmas
        form.estado_7250_ixr.data = inspeccion.estado_7250_ixr
        form.estado_fpfh.data = inspeccion.estado_fpfh
        form.conversor_solar_n1.data = inspeccion.conversor_solar_n1
        form.conversor_solar_n2.data = inspeccion.conversor_solar_n2
        form.limpieza_rack_baterias.data = inspeccion.limpieza_rack_baterias
        form.estado_baterias.data = inspeccion.estado_baterias
        form.estado_inversor.data = inspeccion.estado_inversor
        form.estado_ventiladores.data = inspeccion.estado_ventiladores
        form.limpieza_rack_telecom.data = inspeccion.limpieza_rack_telecom
        form.limpieza_paneles.data = inspeccion.limpieza_paneles
        form.estructura_paneles.data = inspeccion.estructura_paneles
        form.cantidad_cunas.data = inspeccion.cantidad_cunas
        form.checkpoints.data = inspeccion.checkpoints
        form.presion_neumaticos.data = inspeccion.presion_neumaticos
        form.estado_torre.data = inspeccion.estado_torre
        form.estado_piolas_viento.data = inspeccion.estado_piolas_viento
        form.nivelacion_carro.data = inspeccion.nivelacion_carro
        form.gatas_posicionamiento.data = inspeccion.gatas_posicionamiento
        form.manivelas_izaje.data = inspeccion.manivelas_izaje
    
    fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
    return render_template('formularios/inspeccion_cow.html', form=form, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno, editando=True, id_inspeccion=id, inspeccion=inspeccion)

@app.route('/borrar_informe/<int:id>')
def borrar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Solo el técnico que creó el informe o supervisor puede borrar
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para borrar este informe", 403
    
    db.session.delete(inspeccion)
    db.session.commit()
    
    return redirect(url_for('ver_informes'))

@app.route('/generar_pdf/<int:id>')
def generar_pdf(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Verificar permisos
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para generar este PDF", 403
    
    # Crear buffer para PDF
    buffer = BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.7*inch, bottomMargin=0.7*inch,
                           leftMargin=0.7*inch, rightMargin=0.7*inch)
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Estilo para título principal
    titulo_style = ParagraphStyle('TituloStyle', parent=styles['Heading1'],
                                   alignment=TA_CENTER, fontSize=18, 
                                   textColor=colors.HexColor('#0033a0'),
                                   spaceAfter=20, fontName='Helvetica-Bold')
    
    # Estilo para subtítulos
    subtitulo_style = ParagraphStyle('SubtituloStyle', parent=styles['Heading2'],
                                      fontSize=14, textColor=colors.HexColor('#0033a0'),
                                      spaceBefore=15, spaceAfter=10, fontName='Helvetica-Bold')
    
    # Estilo para texto normal
    normal_style = styles['Normal']
    
    # Estilo para celdas de tabla
    cell_style = ParagraphStyle('CellStyle', parent=normal_style, fontSize=9)

        # Estilo para título centrado en tabla
    titulo_tabla_style = ParagraphStyle('TituloTablaStyle', parent=normal_style,
                                         alignment=TA_CENTER, fontSize=11, 
                                         fontName='Helvetica-Bold')
    
    # Contenido del PDF
    elementos = []
    
        # ==================== ENCABEZADO CON LOGOS (TABLA 1x3 CON BORDES) ====================
    
    # Logo Nokia (izquierda)
    try:
        logo_nokia = Image('static/img/nokia_logo.png', width=1.5*inch, height=0.5*inch)
    except:
        logo_nokia = Paragraph("", normal_style)
    
    # Título centrado
    titulo_encabezado = Paragraph("INSPECCIÓN DIARIA COW", 
                                   ParagraphStyle('EncabezadoStyle', parent=normal_style,
                                                 alignment=TA_CENTER, fontSize=14, 
                                                 textColor=colors.HexColor("#000000"),
                                                 fontName='Helvetica-Bold'))
    
    # Logo Sonda (derecha)
    try:
        logo_sonda = Image('static/img/sonda_logo.png', width=1.5*inch, height=0.5*inch)
    except:
        logo_sonda = Paragraph("", normal_style)
    
    # Tabla de 1 fila y 3 columnas CON BORDES NEGROS
    encabezado_tabla = Table([[logo_nokia, titulo_encabezado, logo_sonda]], 
                              colWidths=[2.0*inch, 3.0*inch, 2.0*inch])
    
    encabezado_tabla.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),     # Nokia a la izquierda
        ('ALIGN', (1,0), (1,0), 'CENTER'),   # Título centrado
        ('ALIGN', (2,0), (2,0), 'RIGHT'),    # Sonda a la derecha
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),  # Bordes negros en toda la tabla
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    
    elementos.append(encabezado_tabla)
    elementos.append(Spacer(1, 0.2*inch))
    
    # ==================== DATOS PRINCIPALES ====================
    # Tabla con título centrado y datos en 2 columnas
    datos_principales = [
        [Paragraph("<b>DATOS PRINCIPALES</b>", titulo_tabla_style), ""],
        [Paragraph(f"<b>Responsable:</b> {inspeccion.responsable}", cell_style),
         Paragraph(f"<b>Fecha:</b> {inspeccion.fecha} (Día {inspeccion.dia_turno})", cell_style)],
        [Paragraph(f"<b>Nombre del Sitio:</b> {inspeccion.nombre_sitio}", cell_style),
         Paragraph(f"<b>Hora Inicio:</b> {inspeccion.hora_inicio}", cell_style)],
        [Paragraph(f"<b>Horómetro:</b> {inspeccion.horometro}", cell_style),
         Paragraph(f"<b>Hora Término:</b> {inspeccion.hora_termino}", cell_style)],
    ]
    
    tabla_principales = Table(datos_principales, colWidths=[3.5*inch, 3.5*inch])
    tabla_principales.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),  # Unir celdas para el título
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elementos.append(tabla_principales)
    elementos.append(Spacer(1, 0.2*inch))

        
    
        # ==================== GRUPO ELECTRÓGENO ====================
        # Verificar si es COW Light (no debe mostrar sección GE)
    es_cow_light = 'Light' in inspeccion.nombre_sitio

    # Título dentro de la tabla (combinado)
    if not es_cow_light:
        titulo_ge = Paragraph("Grupo Electrógeno Cummins y Estanque de Combustible", 
                          ParagraphStyle('TituloGEStyle', parent=normal_style,
                                        alignment=TA_CENTER, fontSize=12,
                                        textColor=colors.HexColor("#000000"),
                                        fontName='Helvetica-Bold'))
    
    # Construir tabla GE completa (6 filas de datos + fila estado GE + fila uso GE)
    # Estructura: [Campo1, Valor1, Campo2, OK, NOK]
    
    datos_ge = [
        # Fila 0: Título (combinado)
        [titulo_ge, "", "", ""],
        # Fila 1: Encabezados OK/NOK
        [Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style), 
         Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
        # Fila 2
        [Paragraph("<b>Horas de Funcionamiento</b>", cell_style), 
         Paragraph(str(inspeccion.horas_funcionamiento or '-'), cell_style),
         Paragraph("<b>Limpieza GE Interior</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_ge_interior == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_ge_interior == 'NOK' else "", cell_style)],
        # Fila 3
        [Paragraph("<b>Cantidad de Arranques</b>", cell_style), 
         Paragraph(str(inspeccion.cantidad_arranques or '-'), cell_style),
         Paragraph("<b>Limpieza Radiador</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_radiador == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_radiador == 'NOK' else "", cell_style)],
        # Fila 4
        [Paragraph("<b>Nivel de Aceite</b>", cell_style), 
         Paragraph(inspeccion.nivel_aceite or '-', cell_style),
         Paragraph("<b>Sistema Combustible</b>", cell_style),
         Paragraph("X" if inspeccion.sistema_combustible == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.sistema_combustible == 'NOK' else "", cell_style)],
        # Fila 5
        [Paragraph("<b>Nivel de Combustible</b>", cell_style), 
         Paragraph(inspeccion.nivel_combustible or '-', cell_style),
         Paragraph("<b>Arranque Automático</b>", cell_style),
         Paragraph("X" if inspeccion.arranque_automatico == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.arranque_automatico == 'NOK' else "", cell_style)],
        # Fila 6
        [Paragraph("<b>Nivel de Refrigerante</b>", cell_style), 
         Paragraph(inspeccion.nivel_refrigerante or '-', cell_style),
         Paragraph("<b>Limpieza Interior</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_interior == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_interior == 'NOK' else "", cell_style)],
        # Fila 7
        [Paragraph("<b>Próxima Mantención</b>", cell_style), 
         Paragraph(str(inspeccion.proxima_mantencion or '-'), cell_style),
         Paragraph("<b>Limpieza Exterior</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_exterior == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_exterior == 'NOK' else "", cell_style)],
    ]
    
    # Crear tabla
    tabla_ge = Table(datos_ge, colWidths=[2.8*inch, 0.9*inch, 2.3*inch, 0.5*inch, 0.5*inch])
    tabla_ge.setStyle(TableStyle([
        # Título combinado en la primera fila
        ('SPAN', (0,0), (4,0)),
        ('SPAN', (0,1), (2,1)),  # Combinar las 3 primeras columnas en la fila 1
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
        # Encabezados OK/NOK
        ('TEXTCOLOR', (3,1), (4,1), colors.white),
        # Estilos generales
        ('ALIGN', (0,2), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        # Alinear texto de la primera columna a la izquierda
        ('ALIGN', (0,2), (0,-1), 'LEFT'),
        ('ALIGN', (2,2), (2,-1), 'LEFT'),
    ]))
    
    elementos.append(tabla_ge)
    
    # ==================== TABLA DE ESTADO Y USO GE (6 columnas, como la imagen) ====================
    datos_estado_uso = [
        [Paragraph("<b>Estado de GE Principal</b>", cell_style),
         Paragraph(f"Auto {'✓' if inspeccion.estado_ge_principal == 'Auto' else '✗'}", cell_style),
         Paragraph(f"Shutdown {'✓' if inspeccion.estado_ge_principal == 'Shutdown' else '✗'}", cell_style),
         Paragraph("<b>Cable 5p/4p GE Auxiliar</b>", cell_style),
         Paragraph(f"SI {'✓' if inspeccion.cable_5p_4p == 'SI' else '✗'}", cell_style),
         Paragraph(f"NO {'✓' if inspeccion.cable_5p_4p == 'NO' else '✗'}", cell_style)],
        [Paragraph("<b>Uso de GE Auxiliar</b>", cell_style),
         Paragraph(f"SI {'✓' if inspeccion.uso_ge_auxiliar == 'SI' else '✗'}", cell_style),
         Paragraph(f"NO {'✓' if inspeccion.uso_ge_auxiliar == 'NO' else '✗'}", cell_style),
         Paragraph("<b>Cuenta con adapt. para GE Aux</b>", cell_style),
         Paragraph(f"SI {'✓' if inspeccion.adaptador_ge_aux == 'SI' else '✗'}", cell_style),
         Paragraph(f"NO {'✓' if inspeccion.adaptador_ge_aux == 'NO' else '✗'}", cell_style)],
    ]
    
    tabla_estado_uso = Table(datos_estado_uso, colWidths=[2.0*inch, 0.7*inch, 0.7*inch, 2.0*inch, 0.8*inch, 0.8*inch])
    tabla_estado_uso.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (3,0), (3,0), 'LEFT'),
    ]))
    elementos.append(tabla_estado_uso)
    
        # Tabla con borde para Observaciones y fotos (ancho completo)
    # Observaciones en una sola fila: etiqueta y texto juntos
    texto_observaciones = inspeccion.observaciones_ge or 'Sin observaciones'
    
    datos_obs_fotos = [
        [Paragraph(f"<b>Observaciones:</b> {texto_observaciones}", cell_style)],
    ]
    
            # Agregar fotos dentro del mismo cuadro (título e imagen en la misma celda usando tabla interna)
    fotos_ge = [('foto_1', 'Foto 1'), ('foto_2', 'Foto 2'), ('foto_3', 'Foto 3')]
    for campo, titulo in fotos_ge:
        foto_nombre = getattr(inspeccion, campo, None)
        if foto_nombre:
            ruta_foto = os.path.join('static/uploads', foto_nombre)
            if os.path.exists(ruta_foto):
                try:
                    from reportlab.platypus import Image as ReportLabImage
                    img = ReportLabImage(ruta_foto, width=5*inch, height=3*inch)
                    
                    # Crear tabla interna de 2 filas: título arriba, imagen abajo (pero todo en una celda)
                    contenido_tabla = Table([
                        [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                        [img]
                    ], colWidths=[5.5*inch])
                    contenido_tabla.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 0, colors.white),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ]))
                    
                    datos_obs_fotos.append([contenido_tabla])
                except Exception as e:
                    print(f"Error al cargar foto {campo}: {e}")
            else:
                # Si el archivo no existe, no mostrar nada
                pass
        # Si no hay foto, no se agrega nada
    
    # Crear tabla con bordes negros
    tabla_obs_fotos = Table(datos_obs_fotos, colWidths=[7.0*inch])
    tabla_obs_fotos.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    elementos.append(tabla_obs_fotos)
    elementos.append(Spacer(1, 2.5*inch))
    
        # ==================== RACK ENERGÍA ====================
    # Título dentro de la tabla (combinado)
    titulo_rack = Paragraph("Rack Energía, Telecom y Baterías", 
                            ParagraphStyle('TituloRackStyle', parent=normal_style,
                                          alignment=TA_CENTER, fontSize=12,
                                          textColor=colors.HexColor("#000000"),
                                          fontName='Helvetica-Bold'))
    
    # Construir tabla Rack con 6 columnas: [Campo1, OK, NOK, Campo2, OK, NOK]
    datos_rack = [
        # Fila 0: Título (combinado)
        [titulo_rack, "", "", "", "", ""],
        # Fila 1: Encabezados OK/NOK para ambas secciones
        [Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style),
         Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
        # Fila 2
        [Paragraph("<b>Limpieza Rack Energía</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_energia == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_energia == 'NOK' else "", cell_style),
         Paragraph("<b>Limpieza Rack Telecom</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_telecom == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_telecom == 'NOK' else "", cell_style)],
        # Fila 3
        [Paragraph("<b>Estado Planta Vertiv</b>", cell_style),
         Paragraph("X" if inspeccion.estado_planta_vertiv == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_planta_vertiv == 'NOK' else "", cell_style),
         Paragraph("<b>Estado Air Scale</b>", cell_style),
         Paragraph("X" if inspeccion.estado_air_scale == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_air_scale == 'NOK' else "", cell_style)],
        # Fila 4
        [Paragraph("<b>Rectificador N°1</b>", cell_style),
         Paragraph("X" if inspeccion.rectificador_n1 == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.rectificador_n1 == 'NOK' else "", cell_style),
         Paragraph("<b>Estado de Alarmas</b>", cell_style),
         Paragraph("X" if inspeccion.estado_alarmas == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_alarmas == 'NOK' else "", cell_style)],
        # Fila 5
        [Paragraph("<b>Rectificador N°2</b>", cell_style),
         Paragraph("X" if inspeccion.rectificador_n2 == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.rectificador_n2 == 'NOK' else "", cell_style),
         Paragraph("<b>Estado 7250-IXR</b>", cell_style),
         Paragraph("X" if inspeccion.estado_7250_ixr == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_7250_ixr == 'NOK' else "", cell_style)],
        # Fila 6
        [Paragraph("<b>Rectificador N°3</b>", cell_style),
         Paragraph("X" if inspeccion.rectificador_n3 == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.rectificador_n3 == 'NOK' else "", cell_style),
         Paragraph("<b>Estado FPFH</b>", cell_style),
         Paragraph("X" if inspeccion.estado_fpfh == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_fpfh == 'NOK' else "", cell_style)],
        # Fila 7
        [Paragraph("<b>Conversor Solar N°1</b>", cell_style),
         Paragraph("X" if inspeccion.conversor_solar_n1 == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.conversor_solar_n1 == 'NOK' else "", cell_style),
         Paragraph("<b>Limpieza Rack Baterías</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_baterias == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_rack_baterias == 'NOK' else "", cell_style)],
        # Fila 8
        [Paragraph("<b>Conversor Solar N°2</b>", cell_style),
         Paragraph("X" if inspeccion.conversor_solar_n2 == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.conversor_solar_n2 == 'NOK' else "", cell_style),
         Paragraph("<b>Estado Baterías</b>", cell_style),
         Paragraph("X" if inspeccion.estado_baterias == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_baterias == 'NOK' else "", cell_style)],
        # Fila 9
        [Paragraph("<b>Estado Inversor</b>", cell_style),
         Paragraph("X" if inspeccion.estado_inversor == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_inversor == 'NOK' else "", cell_style),
         Paragraph("<b>Estado Ventiladores</b>", cell_style),
         Paragraph("X" if inspeccion.estado_ventiladores == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_ventiladores == 'NOK' else "", cell_style)],
    ]
    
    # Crear tabla (6 columnas)
    tabla_rack = Table(datos_rack, colWidths=[2.7*inch, 0.5*inch, 0.5*inch, 2.3*inch, 0.5*inch, 0.5*inch])
    tabla_rack.setStyle(TableStyle([
        # Título combinado en la primera fila
        ('SPAN', (0,0), (5,0)),
        # Combinar las primeras 3 columnas en la fila 1 para alinear encabezados
        ('SPAN', (0,1), (0,1)),
        ('SPAN', (3,1), (3,1)),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
        # Encabezados OK/NOK
        ('BACKGROUND', (1,1), (2,1), colors.white),
        ('BACKGROUND', (4,1), (5,1), colors.white),
        ('TEXTCOLOR', (1,1), (2,1), colors.black),
        ('TEXTCOLOR', (4,1), (5,1), colors.black),
        # Estilos generales
        ('ALIGN', (1,2), (5,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        # Alinear textos de la primera columna a la izquierda
        ('ALIGN', (0,2), (0,-1), 'LEFT'),
        ('ALIGN', (3,2), (3,-1), 'LEFT'),
    ]))
    
    elementos.append(tabla_rack)
    
    # ==================== OBSERVACIONES Y FOTOS RACK (igual que GE) ====================
    texto_observaciones_rack = inspeccion.observaciones_rack or 'Sin observaciones'
    
    datos_obs_fotos_rack = [
        [Paragraph(f"<b>Observaciones:</b> {texto_observaciones_rack}", cell_style)],
    ]
    
    # Agregar fotos del Rack
    fotos_rack_lista = [('foto_rack_1', 'Foto Rack 1'), ('foto_rack_2', 'Foto Rack 2'), ('foto_rack_3', 'Foto Rack 3')]
    for campo, titulo in fotos_rack_lista:
        foto_nombre = getattr(inspeccion, campo, None)
        if foto_nombre:
            ruta_foto = os.path.join('static/uploads', foto_nombre)
            if os.path.exists(ruta_foto):
                try:
                    from reportlab.platypus import Image as ReportLabImage
                    img = ReportLabImage(ruta_foto, width=5*inch, height=3*inch)
                    
                    contenido_tabla = Table([
                        [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                        [img]
                    ], colWidths=[5.5*inch])
                    contenido_tabla.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 0, colors.white),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ]))
                    
                    datos_obs_fotos_rack.append([contenido_tabla])
                except Exception as e:
                    print(f"Error al cargar foto {campo}: {e}")
    
    # Crear tabla con bordes negros
    tabla_obs_fotos_rack = Table(datos_obs_fotos_rack, colWidths=[7.0*inch])
    tabla_obs_fotos_rack.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    elementos.append(tabla_obs_fotos_rack)
    elementos.append(Spacer(1, 2.0*inch))
    
        # ==================== ESTRUCTURAS ====================
    # Título dentro de la tabla (combinado)
    titulo_estructuras = Paragraph("Estructuras, Paneles Solares, Piolas de Viento, Neumáticos y otros", 
                                    ParagraphStyle('TituloEstructurasStyle', parent=normal_style,
                                                  alignment=TA_CENTER, fontSize=12,
                                                  textColor=colors.HexColor("#000000"),
                                                  fontName='Helvetica-Bold'))
    
    # Construir tabla Estructuras con 6 columnas: [Campo1, OK, NOK, Campo2, OK, NOK]
    datos_estructuras = [
        # Fila 0: Título (combinado)
        [titulo_estructuras, "", "", "", "", ""],
        # Fila 1: Encabezados OK/NOK para ambas secciones
        [Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style),
         Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
        # Fila 2
        [Paragraph("<b>Limpieza de Paneles</b>", cell_style),
         Paragraph("X" if inspeccion.limpieza_paneles == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.limpieza_paneles == 'NOK' else "", cell_style),
         Paragraph("<b>Estado de Torre</b>", cell_style),
         Paragraph("X" if inspeccion.estado_torre == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_torre == 'NOK' else "", cell_style)],
        # Fila 3
        [Paragraph("<b>Estructura de P. Solares</b>", cell_style),
         Paragraph("X" if inspeccion.estructura_paneles == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estructura_paneles == 'NOK' else "", cell_style),
         Paragraph("<b>Estado Piolas de Viento</b>", cell_style),
         Paragraph("X" if inspeccion.estado_piolas_viento == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.estado_piolas_viento == 'NOK' else "", cell_style)],
        # Fila 4
        [Paragraph("<b>Cantidad de Cuñas</b>", cell_style),
         Paragraph(str(inspeccion.cantidad_cunas or '-'), cell_style),
         Paragraph("", cell_style),
         Paragraph("<b>Nivelación del Carro</b>", cell_style),
         Paragraph("X" if inspeccion.nivelacion_carro == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.nivelacion_carro == 'NOK' else "", cell_style)],
        # Fila 5
        [Paragraph("<b>Checkpoints</b>", cell_style),
         Paragraph("X" if inspeccion.checkpoints == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.checkpoints == 'NOK' else "", cell_style),
         Paragraph("<b>Gatas de Posicionamiento</b>", cell_style),
         Paragraph("X" if inspeccion.gatas_posicionamiento == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.gatas_posicionamiento == 'NOK' else "", cell_style)],
        # Fila 6
        [Paragraph("<b>Presión de Neumáticos</b>", cell_style),
         Paragraph("X" if inspeccion.presion_neumaticos == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.presion_neumaticos == 'NOK' else "", cell_style),
         Paragraph("<b>Manivelas Izaje de Gatas</b>", cell_style),
         Paragraph("X" if inspeccion.manivelas_izaje == 'OK' else "", cell_style),
         Paragraph("X" if inspeccion.manivelas_izaje == 'NOK' else "", cell_style)],
    ]
    
    # Crear tabla (6 columnas)
    tabla_estructuras = Table(datos_estructuras, colWidths=[2.7*inch, 0.5*inch, 0.5*inch, 2.3*inch, 0.5*inch, 0.5*inch])
    tabla_estructuras.setStyle(TableStyle([
        # Título combinado en la primera fila
        ('SPAN', (0,0), (5,0)),
        # Combinar las primeras 3 columnas en la fila 1 para alinear encabezados
        ('SPAN', (0,1), (0,1)),
        ('SPAN', (3,1), (3,1)),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
        # Estilos generales
        ('ALIGN', (1,2), (5,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        # Alinear textos de la primera columna a la izquierda
        ('ALIGN', (0,2), (0,-1), 'LEFT'),
        ('ALIGN', (3,2), (3,-1), 'LEFT'),
    ]))
    
    elementos.append(tabla_estructuras)
    
    # ==================== OBSERVACIONES Y FOTOS ESTRUCTURAS ====================
    texto_observaciones_estructuras = inspeccion.observaciones_estructuras or 'Sin observaciones'
    
    datos_obs_fotos_estructuras = [
        [Paragraph(f"<b>Observaciones:</b> {texto_observaciones_estructuras}", cell_style)],
    ]
    
    # Agregar fotos de Estructuras
    fotos_estructuras_lista = [('foto_estructuras_1', 'Foto Estructura 1'), 
                                ('foto_estructuras_2', 'Foto Estructura 2'), 
                                ('foto_estructuras_3', 'Foto Estructura 3')]
    for campo, titulo in fotos_estructuras_lista:
        foto_nombre = getattr(inspeccion, campo, None)
        if foto_nombre:
            ruta_foto = os.path.join('static/uploads', foto_nombre)
            if os.path.exists(ruta_foto):
                try:
                    from reportlab.platypus import Image as ReportLabImage
                    img = ReportLabImage(ruta_foto, width=5*inch, height=3*inch)
                    
                    contenido_tabla = Table([
                        [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                        [img]
                    ], colWidths=[5.5*inch])
                    contenido_tabla.setStyle(TableStyle([
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('GRID', (0,0), (-1,-1), 0, colors.white),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ]))
                    
                    datos_obs_fotos_estructuras.append([contenido_tabla])
                except Exception as e:
                    print(f"Error al cargar foto {campo}: {e}")
    
    # Crear tabla con bordes negros
    tabla_obs_fotos_estructuras = Table(datos_obs_fotos_estructuras, colWidths=[7.0*inch])
    tabla_obs_fotos_estructuras.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    elementos.append(tabla_obs_fotos_estructuras)
    elementos.append(Spacer(1, 2.0*inch))

        # ==================== LEVANTAMIENTO DE FOTOGRAFÍAS (33 PUNTOS) ====================
    # Título principal de la sección DENTRO DE UNA TABLA
    titulo_levantamiento = Paragraph("Levantamiento de Fotografías", 
                                      ParagraphStyle('TituloLevantamientoStyle', parent=normal_style,
                                                    alignment=TA_CENTER, fontSize=12,
                                                    textColor=colors.HexColor("#000000"),
                                                    fontName='Helvetica-Bold'))
    
    tabla_titulo_lev = Table([[titulo_levantamiento]], colWidths=[7.0*inch])
    tabla_titulo_lev.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elementos.append(tabla_titulo_lev)
    
    def crear_tabla_foto(titulo, foto_nombre):
        """Crea una tabla con título y una sola imagen (solo si hay foto válida)"""
        # Si no hay foto, no mostrar nada
        if not foto_nombre:
            return None
        
        ruta_foto = os.path.join('static/uploads', foto_nombre)
        if not os.path.exists(ruta_foto):
            return None
        
        try:
            img = ReportLabImage(ruta_foto, width=5*inch, height=3*inch)
            contenido_celda = [
                Paragraph(f"<b>{titulo}</b>", cell_style),
                img
            ]
            
            tabla_foto = Table([[contenido_celda]], colWidths=[7.0*inch])
            tabla_foto.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            return tabla_foto
        except:
            return None
    
    # Lista de 33 títulos con sus campos correspondientes
    puntos_fotos = [
        (1, "1. Fotografía del estado del sitio previo al comienzo de trabajos (recordar llamar a NOC informando el ingreso):", 'foto_levantamiento_1'),
        (2, "2. Fotografía del panel de control del generador donde se observa el indicador de modo automático encendido:", 'foto_levantamiento_2'),
        (3, "3. Ingrese fotografía de plan de mantenimiento del generador:", 'foto_levantamiento_3'),
        (4, "4. Fotografía del nivel de aceite:", 'foto_levantamiento_4'),
        (5, "5. Fotografía del nivel de combustible:", 'foto_levantamiento_5'),
        (6, "6. Foto del refrigerante del generador:", 'foto_levantamiento_6'),
        (7, "7. Ingresar fotografía del estado inicial de planta vertiv:", 'foto_levantamiento_7'),
        (8, "8. Fotografía de la pantalla de la planta rectificadora donde se observa la entrada de corriente alterna:", 'foto_levantamiento_8'),
        (9, "9. Ingresar fotografía del estado de los conversores de planta vertiv:", 'foto_levantamiento_9'),
        (10, "10. Ingresar fotografía del estado de los rectificadores de planta vertiv:", 'foto_levantamiento_10'),
        (11, "11. Ingresar fotografía del voltaje de salida dc, todo lo que alimenta la vertiv:", 'foto_levantamiento_11'),
        (12, "12. Ingresar fotografía del estado de carga de batería planta vertiv (a):", 'foto_levantamiento_12'),
        (13, "13. Ingresar fotografía del estado de carga de batería planta vertiv (b):", 'foto_levantamiento_13'),
        (14, "14. Fotografía del rack de energía antes:", 'foto_levantamiento_14'),
        (15, "15. Fotografía del rack de energía después:", 'foto_levantamiento_15'),
        (16, "16. Fotografía del rack de telecomunicaciones antes:", 'foto_levantamiento_16'),
        (17, "17. Fotografía del rack de telecomunicaciones después:", 'foto_levantamiento_17'),
        (18, "18. Ingresar fotografía filtro IXR antes:", 'foto_levantamiento_18'),
        (19, "19. Ingresar fotografía filtro IXR después:", 'foto_levantamiento_19'),
        (20, "20. Fotografía de rack de baterías N°1 antes:", 'foto_levantamiento_20'),
        (21, "21. Fotografía de rack de baterías N°1 después:", 'foto_levantamiento_21'),
        (22, "22. Fotografía de rack de baterías N°2 antes:", 'foto_levantamiento_22'),
        (23, "23. Fotografía de rack de baterías N°2 después:", 'foto_levantamiento_23'),
        (24, "24. Fotografía de paneles solares antes:", 'foto_levantamiento_24'),
        (25, "25. Fotografía de paneles solares después:", 'foto_levantamiento_25'),
        (26, "26. Fotografía de estructura torre:", 'foto_levantamiento_26'),
        (27, "27. Ingresar fotografía de la antena:", 'foto_levantamiento_27'),
        (28, "28. Fotografía de vientos (a):", 'foto_levantamiento_28'),
        (29, "29. Fotografía de vientos (b):", 'foto_levantamiento_29'),
        (30, "30. Fotografía de vientos (c):", 'foto_levantamiento_30'),
        (31, "31. Ingresar fotografía de neumáticos (a):", 'foto_levantamiento_31'),
        (32, "32. Ingresar fotografía de neumáticos (b):", 'foto_levantamiento_32'),
        (33, "33. Fotografía del sitio al término de los trabajos (Recordar llamar a NOC, informando la salida del sitio):", 'foto_levantamiento_33'),
    ]
    
    # Generar cada punto (solo si hay foto)
    for num, titulo, campo_foto in puntos_fotos:
        foto_nombre = getattr(inspeccion, campo_foto, None)
        tabla = crear_tabla_foto(titulo, foto_nombre)
        if tabla is not None:  # Solo agregar si hay foto
            elementos.append(tabla)

        # ==================== LEVANTAMIENTO FOTOGRAFÍAS DE MEJORAS ====================
    # Verificar si existe al menos una mejora (descripción o foto)
    mejoras_lista = [
        (inspeccion.descripcion_mejora_1, inspeccion.foto_mejora_1),
        (inspeccion.descripcion_mejora_2, inspeccion.foto_mejora_2),
        (inspeccion.descripcion_mejora_3, inspeccion.foto_mejora_3),
        (inspeccion.descripcion_mejora_4, inspeccion.foto_mejora_4),
    ]
    
    # Verificar si hay al menos una mejora con contenido
    hay_mejoras = any(descripcion or foto for descripcion, foto in mejoras_lista)
    
    if hay_mejoras:
        # Título principal de la sección DENTRO DE UNA TABLA
        titulo_mejoras = Paragraph("Levantamiento fotografías de mejoras:", 
                                    ParagraphStyle('TituloMejorasStyle', parent=normal_style,
                                                  alignment=TA_CENTER, fontSize=12,
                                                  textColor=colors.HexColor("#000000"),
                                                  fontName='Helvetica-Bold'))
        
        tabla_titulo_mejoras = Table([[titulo_mejoras]], colWidths=[7.0*inch])
        tabla_titulo_mejoras.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elementos.append(tabla_titulo_mejoras)
        
        def crear_tabla_mejora(descripcion, foto_nombre):
            """Crea una tabla con descripción de mejora y su imagen"""
            contenido_celda = []
            
            # Agregar descripción (si existe)
            if descripcion and descripcion.strip():
                contenido_celda.append(Paragraph(f"<b>Mejora:</b> {descripcion}", cell_style))
            else:
                contenido_celda.append(Paragraph("<b>Mejora:</b> (Sin descripción)", cell_style))
            
            # Agregar foto si existe
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = ReportLabImage(ruta_foto, width=5*inch, height=3*inch)
                        contenido_celda.append(img)
                    except:
                        contenido_celda.append(Paragraph("(Error al cargar imagen)", cell_style))
                else:
                    contenido_celda.append(Paragraph("(No se encontró la imagen)", cell_style))
            else:
                contenido_celda.append(Paragraph("(Sin foto)", cell_style))
            
            tabla_mejora = Table([[contenido_celda]], colWidths=[7.0*inch])
            tabla_mejora.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('LEFTPADDING', (0,0), (-1,-1), 8),
                ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ]))
            return tabla_mejora
        
        # Generar cada mejora
        for descripcion, foto_nombre in mejoras_lista:
            if descripcion or foto_nombre:
                elementos.append(crear_tabla_mejora(descripcion or '', foto_nombre))
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    # Nombre del archivo: nombre_del_sitio_fecha.pdf
    nombre_base = inspeccion.nombre_sitio.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{nombre_base}_{inspeccion.fecha.replace('/', '-')}.pdf"
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# 6. SEXTO crear tablas
with app.app_context():
    db.create_all()

# 7. SÉPTIMO ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)

# Configuración para carga de imágenes (sin flask-uploads)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS