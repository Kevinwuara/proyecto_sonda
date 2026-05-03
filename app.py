from flask import Flask, render_template, redirect, url_for, request, session, send_file, jsonify
from wtforms import form
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import check_password_hash
from forms_cow import InspeccionCOWForm
from forms_ge import InspeccionGEForm
from werkzeug.utils import secure_filename
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

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

    def __repr__(self):
        return f'<Usuario {self.username}>'

# Modelo de Inspección COW
class InspeccionCOW(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sitio_id = db.Column(db.Integer, db.ForeignKey('sitio.id'), nullable=True)
    fecha = db.Column(db.String(20), nullable=False)
    dia_turno = db.Column(db.Integer, nullable=False)
    responsable = db.Column(db.String(50), nullable=False)
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

    # Motivo de Rechazo
    motivo_rechazo = db.Column(db.String(500), nullable=True)

    # Estado y control
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aprobado, rechazado
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    usuario = db.relationship('Usuario', backref='inspecciones_cow')
    
    def __repr__(self):
        return f'<InspeccionCOW {self.id} - {self.nombre_sitio}>'
    
    # Modelo de Sitio (catálogo de COWs)
class Sitio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_sitio = db.Column(db.String(150), unique=True, nullable=False)
    area = db.Column(db.String(50), nullable=True)  # Ej: "Área Autónoma", "Área Convencional", "Fuera Área Mina"
    tipo = db.Column(db.String(20), nullable=True)  # Ej: "HD", "LIGHT", "FAST SITE"
    ubicacion = db.Column(db.String(100), nullable=True)  # Ej: "Esperanza Sur", "OXE Encuentro"
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con InspeccionCOW (un sitio tiene muchas inspecciones)
    inspecciones = db.relationship('InspeccionCOW', backref='sitio_ref', lazy=True)
    
    def __repr__(self):
        return f'<Sitio {self.nombre_sitio}>'
    
# Modelo de Fotografia (normalizado)
class Fotografia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspeccion_id = db.Column(db.Integer, db.ForeignKey('inspeccion_cow.id'), nullable=False)
    seccion = db.Column(db.String(50), nullable=False)  # 'ge', 'rack', 'estructura', 'levantamiento', 'mejora'
    punto_numero = db.Column(db.Integer, nullable=True)  # 1-33 para levantamiento, 1-4 para mejoras
    titulo = db.Column(db.String(200), nullable=True)  # Para descripción de mejoras
    ruta_archivo = db.Column(db.String(200), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    inspeccion = db.relationship('InspeccionCOW', backref='fotografias', lazy=True)
    
    def __repr__(self):
        return f'<Fotografia {self.seccion}_{self.punto_numero}>'

        # Modelo de Mejora (normalizado, 4 mejoras por inspección)
class Mejora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inspeccion_id = db.Column(db.Integer, db.ForeignKey('inspeccion_cow.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)  # 1, 2, 3, 4
    descripcion = db.Column(db.String(500), nullable=True)
    ruta_foto = db.Column(db.String(200), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    inspeccion = db.relationship('InspeccionCOW', backref='mejoras', lazy=True)
    
    def __repr__(self):
        return f'<Mejora {self.numero} de inspección {self.inspeccion_id}>'

        

def calcular_fecha_turno(fecha_ingresada=None):
    # Si se ingresa una fecha (desde el formulario), usarla; si no, usar hoy
    if fecha_ingresada:
        hoy = datetime.strptime(fecha_ingresada, '%Y-%m-%d')
    else:
        hoy = datetime.now()

    fecha_str = hoy.strftime('%d/%m/%Y')
    fecha_iso = hoy.strftime('%Y-%m-%d')

    # Fecha base: 01/04/2026
    fecha_base = datetime(2026, 4, 1)
    diferencia = (hoy - fecha_base).days

    # Cada ciclo completo son 14 días
    dia_en_ciclo = diferencia % 14

    if dia_en_ciclo < 7:
        turno = "A"
        dia_turno = dia_en_ciclo + 1
        estado = f"Turno A 7x7: Día {dia_turno} de trabajo"
    else:
        turno = "B"
        dia_turno = dia_en_ciclo - 6
        estado = f"Turno B 7x7: Día {dia_turno} de trabajo"

    return fecha_str, fecha_iso, dia_turno, turno, estado

    # Modelo de Inspección GE Auxiliar
class InspeccionGE(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sitio_id = db.Column(db.Integer, db.ForeignKey('sitio.id'), nullable=True)
    fecha = db.Column(db.String(20), nullable=False)
    dia_turno = db.Column(db.Integer, nullable=False)
    
    # Datos Generales
    responsable = db.Column(db.String(50), nullable=False)
    nombre_ge = db.Column(db.String(50), nullable=False)
    tipo_ge = db.Column(db.String(50), nullable=False)
    horometro = db.Column(db.Integer, nullable=False)
    hora_inicio = db.Column(db.String(10), nullable=False)
    hora_termino = db.Column(db.String(10), nullable=False)
    potencia_continua = db.Column(db.Integer, nullable=True)
    
    # Grupo Electrógeno y Estanque
    cantidad_arranques = db.Column(db.Integer, nullable=False)
    horas_funcionamiento = db.Column(db.Integer, nullable=False)
    nivel_aceite = db.Column(db.String(10), nullable=False)
    nivel_combustible = db.Column(db.String(10), nullable=False)
    nivel_refrigerante = db.Column(db.String(10), nullable=False)
    proxima_mantencion = db.Column(db.Integer, nullable=False)
    estado_carcasa = db.Column(db.String(5), nullable=False)
    limpieza_ge_interior = db.Column(db.String(5), nullable=False)
    limpieza_radiador = db.Column(db.String(5), nullable=False)
    visor_combustible = db.Column(db.String(5), nullable=False)
    arranque_automatico = db.Column(db.String(5), nullable=False)
    limpieza_interior = db.Column(db.String(5), nullable=False)
    limpieza_exterior = db.Column(db.String(5), nullable=False)
    cable_5p_4p = db.Column(db.String(5), nullable=False)
    observaciones = db.Column(db.Text, nullable=True)
    
    # Estado Breaker y Baterías
    estado_pantalla = db.Column(db.String(5), nullable=False)
    estado_parada_emergencia = db.Column(db.String(5), nullable=False)
    estado_corta_corriente = db.Column(db.String(5), nullable=False)
    estado_selector = db.Column(db.String(5), nullable=False)
    estado_bornes_bateria = db.Column(db.String(5), nullable=False)
    estado_ramal_cables = db.Column(db.String(5), nullable=False)
    estado_enchufe = db.Column(db.String(5), nullable=False)
    estado_cebador = db.Column(db.String(5), nullable=False)
    estado_mangueras = db.Column(db.String(5), nullable=False)
    estado_alarmas = db.Column(db.String(5), nullable=False)
    estado_extintor = db.Column(db.String(5), nullable=False)
    estado_puertas = db.Column(db.String(5), nullable=False)
    estado_baterias = db.Column(db.String(5), nullable=False)
    estado_ventilador = db.Column(db.String(5), nullable=False)
    observaciones_breaker = db.Column(db.Text, nullable=True)
    
    # Estructuras, Chasis y Otros
    limpieza_general = db.Column(db.String(5), nullable=False)
    estado_chasis = db.Column(db.String(5), nullable=False)
    cantidad_cunas = db.Column(db.String(10), nullable=False)
    checkpoints = db.Column(db.String(5), nullable=False)
    presion_neumaticos = db.Column(db.String(5), nullable=False)
    estado_jaula = db.Column(db.String(5), nullable=False)
    estado_candados = db.Column(db.String(5), nullable=False)
    nivelacion_carro = db.Column(db.String(5), nullable=False)
    patas_posicionamiento = db.Column(db.String(5), nullable=False)
    manivelas_izajes = db.Column(db.String(5), nullable=False)
    observaciones_estructuras = db.Column(db.Text, nullable=True)
    
    # Fotografías (rutas)
    foto_1 = db.Column(db.String(200), nullable=True)
    foto_2 = db.Column(db.String(200), nullable=True)
    foto_3 = db.Column(db.String(200), nullable=True)
    foto_breaker_1 = db.Column(db.String(200), nullable=True)
    foto_breaker_2 = db.Column(db.String(200), nullable=True)
    foto_breaker_3 = db.Column(db.String(200), nullable=True)
    foto_estructura_1 = db.Column(db.String(200), nullable=True)
    foto_estructura_2 = db.Column(db.String(200), nullable=True)
    foto_estructura_3 = db.Column(db.String(200), nullable=True)
    foto_lev_1 = db.Column(db.String(200), nullable=True)
    foto_lev_2 = db.Column(db.String(200), nullable=True)
    foto_lev_3 = db.Column(db.String(200), nullable=True)
    foto_lev_4 = db.Column(db.String(200), nullable=True)
    foto_lev_5 = db.Column(db.String(200), nullable=True)
    foto_lev_6 = db.Column(db.String(200), nullable=True)
    foto_lev_7 = db.Column(db.String(200), nullable=True)
    foto_lev_8 = db.Column(db.String(200), nullable=True)
    
    # Estado y control
    estado = db.Column(db.String(20), default='pendiente')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    motivo_rechazo = db.Column(db.String(500), nullable=True)
    
    # Relaciones
    usuario = db.relationship('Usuario', backref='inspecciones_ge')
    sitio = db.relationship('Sitio', backref='inspecciones_ge')
    
    def __repr__(self):
        return f'<InspeccionGE {self.id} - {self.nombre_ge}>'

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

        # Cargar opciones de sitios desde la base de datos
    sitios = Sitio.query.filter_by(activo=True).all()
    form.nombre_sitio.choices = [(str(s.id), s.nombre_sitio) for s in sitios]

    # Inicializar variables
    fecha_actual = None
    fecha_iso = None
    dia_turno = None
    turno = None
    estado_turno = None
    
    if request.method == 'POST' and form.validate_on_submit():
        print("=== VALORES RECIBIDOS ===")
        print(f"obs_ge: '{form.observaciones_ge.data}'")
        print(f"obs_rack: '{form.observaciones_rack.data}'")
        print(f"obs_est: '{form.observaciones_estructuras.data}'")
        print("========================")
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
            sitio_id=int(form.nombre_sitio.data),
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

        print("=== VALORES ASIGNADOS ===")
        print(f"obs_ge: '{nueva_inspeccion.observaciones_ge}'")
        print(f"obs_rack: '{nueva_inspeccion.observaciones_rack}'")
        print(f"obs_est: '{nueva_inspeccion.observaciones_estructuras}'")
        print("========================")
        
                # Guardar la inspección primero
        db.session.add(nueva_inspeccion)
        db.session.commit()  # ← Esto asigna el ID a nueva_inspeccion.id

                # Verificar que se guardó en la BD
        inspeccion_guardada = InspeccionCOW.query.get(nueva_inspeccion.id)
        print("=== VERIFICACIÓN POST-COMMIT ===")
        print(f"ID: {inspeccion_guardada.id}")
        print(f"obs_ge en BD: '{inspeccion_guardada.observaciones_ge}'")
        print(f"obs_rack en BD: '{inspeccion_guardada.observaciones_rack}'")
        print(f"obs_est en BD: '{inspeccion_guardada.observaciones_estructuras}'")
        print("================================")
        
        # ==================== AHORA SÍ, GUARDAR FOTOGRAFÍAS ====================
        # (después del commit, cuando el ID ya existe)
        
        # 1. Fotos GE
        for i, foto_nombre in enumerate(fotos_guardadas, 1):
            if foto_nombre:
                foto = Fotografia(
                    inspeccion_id=nueva_inspeccion.id,  # ← Ahora tiene ID válido
                    seccion='ge',
                    punto_numero=i,
                    ruta_archivo=foto_nombre
                )
                db.session.add(foto)
        
        # 2. Fotos Rack
        for i, foto_nombre in enumerate(fotos_rack, 1):
            if foto_nombre:
                foto = Fotografia(
                    inspeccion_id=nueva_inspeccion.id,
                    seccion='rack',
                    punto_numero=i,
                    ruta_archivo=foto_nombre
                )
                db.session.add(foto)
        
        # 3. Fotos Estructuras
        for i, foto_nombre in enumerate(fotos_estructuras, 1):
            if foto_nombre:
                foto = Fotografia(
                    inspeccion_id=nueva_inspeccion.id,
                    seccion='estructura',
                    punto_numero=i,
                    ruta_archivo=foto_nombre
                )
                db.session.add(foto)
        
        # 4. Fotos Levantamiento
        for i, foto_nombre in enumerate(fotos_levantamiento, 1):
            if foto_nombre and foto_nombre != 'None':
                foto = Fotografia(
                    inspeccion_id=nueva_inspeccion.id,
                    seccion='levantamiento',
                    punto_numero=i,
                    ruta_archivo=foto_nombre
                )
                db.session.add(foto)
        
        # 5. Fotos Mejoras
        for i, foto_nombre in enumerate(fotos_mejora, 1):
            if foto_nombre and foto_nombre != 'None':
                desc = descripciones_mejora[i-1] if i-1 < len(descripciones_mejora) else ''
                foto = Fotografia(
                    inspeccion_id=nueva_inspeccion.id,
                    seccion='mejora',
                    punto_numero=i,
                    titulo=desc,
                    ruta_archivo=foto_nombre
                )
                db.session.add(foto)

        # Guardar Mejoras en tabla normalizada
        for i in range(1, 5):
            desc = descripciones_mejora[i-1] if i-1 < len(descripciones_mejora) else ''
            foto = fotos_mejora[i-1] if i-1 < len(fotos_mejora) else None
            
            mejora = Mejora(
                inspeccion_id=nueva_inspeccion.id,
                numero=i,
                descripcion=desc,
                ruta_foto=foto
            )
            db.session.add(mejora)
        
        # Guardar todas las fotos
        db.session.commit()

        mensaje = f"Inspección COW guardada correctamente (ID: {nueva_inspeccion.id})"
        return render_template('formularios/inspeccion_cow.html', form=form, mensaje=mensaje, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)
    
    # GET request
    fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
    return render_template('formularios/inspeccion_cow.html', form=form, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)

@app.route('/inspeccion_ge', methods=['GET', 'POST'])
def inspeccion_ge():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    form = InspeccionGEForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        fecha_seleccionada = request.form.get('fecha')
        if fecha_seleccionada:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno(fecha_seleccionada)
        else:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
        
        # Procesar fotos (tu código existente aquí...)
        fotos_guardadas = []
        for i in range(1, 4):
            campo_foto = f'foto_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ge_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_guardadas.append(filename)
                else:
                    fotos_guardadas.append(None)
            else:
                fotos_guardadas.append(None)
        
        # Procesar fotos breaker
        fotos_breaker = []
        for i in range(1, 4):
            campo_foto = f'foto_breaker_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ge_breaker_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_breaker.append(filename)
                else:
                    fotos_breaker.append(None)
            else:
                fotos_breaker.append(None)
        
        # Procesar fotos estructuras
        fotos_estructuras = []
        for i in range(1, 4):
            campo_foto = f'foto_estructura_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ge_estructura_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_estructuras.append(filename)
                else:
                    fotos_estructuras.append(None)
            else:
                fotos_estructuras.append(None)
        
        # Procesar fotos levantamiento (8 puntos)
        fotos_levantamiento = []
        for i in range(1, 9):
            campo_foto = f'foto_lev_{i}'
            if campo_foto in request.files:
                file = request.files[campo_foto]
                if file and file.filename:
                    filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ge_lev_{i}.jpg")
                    filepath = os.path.join('static/uploads', filename)
                    file.save(filepath)
                    fotos_levantamiento.append(filename)
                else:
                    fotos_levantamiento.append(None)
            else:
                fotos_levantamiento.append(None)
        
        # Guardar en base de datos
        usuario_actual = Usuario.query.filter_by(username=session['username']).first()
        
        nueva_inspeccion_ge = InspeccionGE(
            usuario_id=usuario_actual.id,
            sitio_id=None,
            fecha=fecha_actual,
            dia_turno=dia_turno,
            responsable=form.responsable.data,
            nombre_ge=form.nombre_ge.data,
            tipo_ge=form.tipo_ge.data,
            horometro=form.horometro.data,
            hora_inicio=form.hora_inicio.data,
            hora_termino=form.hora_termino.data,
            potencia_continua=form.potencia_continua.data,
            cantidad_arranques=form.cantidad_arranques.data,
            horas_funcionamiento=form.horas_funcionamiento.data,
            nivel_aceite=form.nivel_aceite.data,
            nivel_combustible=form.nivel_combustible.data,
            nivel_refrigerante=form.nivel_refrigerante.data,
            proxima_mantencion=form.proxima_mantencion.data,
            estado_carcasa=form.estado_carcasa.data,
            limpieza_ge_interior=form.limpieza_ge_interior.data,
            limpieza_radiador=form.limpieza_radiador.data,
            visor_combustible=form.visor_combustible.data,
            arranque_automatico=form.arranque_automatico.data,
            limpieza_interior=form.limpieza_interior.data,
            limpieza_exterior=form.limpieza_exterior.data,
            cable_5p_4p=form.cable_5p_4p.data,
            observaciones=form.observaciones.data,
            estado_pantalla=form.estado_pantalla.data,
            estado_parada_emergencia=form.estado_parada_emergencia.data,
            estado_corta_corriente=form.estado_corta_corriente.data,
            estado_selector=form.estado_selector.data,
            estado_bornes_bateria=form.estado_bornes_bateria.data,
            estado_ramal_cables=form.estado_ramal_cables.data,
            estado_enchufe=form.estado_enchufe.data,
            estado_cebador=form.estado_cebador.data,
            estado_mangueras=form.estado_mangueras.data,
            estado_alarmas=form.estado_alarmas.data,
            estado_extintor=form.estado_extintor.data,
            estado_puertas=form.estado_puertas.data,
            estado_baterias=form.estado_baterias.data,
            estado_ventilador=form.estado_ventilador.data,
            observaciones_breaker=form.observaciones_breaker.data,
            limpieza_general=form.limpieza_general.data,
            estado_chasis=form.estado_chasis.data,
            cantidad_cunas=form.cantidad_cunas.data,
            checkpoints=form.checkpoints.data,
            presion_neumaticos=form.presion_neumaticos.data,
            estado_jaula=form.estado_jaula.data,
            estado_candados=form.estado_candados.data,
            nivelacion_carro=form.nivelacion_carro.data,
            patas_posicionamiento=form.patas_posicionamiento.data,
            manivelas_izajes=form.manivelas_izajes.data,
            observaciones_estructuras=form.observaciones_estructuras.data,
            foto_1=fotos_guardadas[0] if len(fotos_guardadas) > 0 else None,
            foto_2=fotos_guardadas[1] if len(fotos_guardadas) > 1 else None,
            foto_3=fotos_guardadas[2] if len(fotos_guardadas) > 2 else None,
            foto_breaker_1=fotos_breaker[0] if len(fotos_breaker) > 0 else None,
            foto_breaker_2=fotos_breaker[1] if len(fotos_breaker) > 1 else None,
            foto_breaker_3=fotos_breaker[2] if len(fotos_breaker) > 2 else None,
            foto_estructura_1=fotos_estructuras[0] if len(fotos_estructuras) > 0 else None,
            foto_estructura_2=fotos_estructuras[1] if len(fotos_estructuras) > 1 else None,
            foto_estructura_3=fotos_estructuras[2] if len(fotos_estructuras) > 2 else None,
            foto_lev_1=fotos_levantamiento[0] if len(fotos_levantamiento) > 0 else None,
            foto_lev_2=fotos_levantamiento[1] if len(fotos_levantamiento) > 1 else None,
            foto_lev_3=fotos_levantamiento[2] if len(fotos_levantamiento) > 2 else None,
            foto_lev_4=fotos_levantamiento[3] if len(fotos_levantamiento) > 3 else None,
            foto_lev_5=fotos_levantamiento[4] if len(fotos_levantamiento) > 4 else None,
            foto_lev_6=fotos_levantamiento[5] if len(fotos_levantamiento) > 5 else None,
            foto_lev_7=fotos_levantamiento[6] if len(fotos_levantamiento) > 6 else None,
            foto_lev_8=fotos_levantamiento[7] if len(fotos_levantamiento) > 7 else None,
            estado='pendiente'
        )
        
        db.session.add(nueva_inspeccion_ge)
        db.session.commit()
        
        mensaje = f"Inspección GE Auxiliar guardada correctamente (ID: {nueva_inspeccion_ge.id})"
        return render_template('formularios/inspeccion_ge.html', form=form, mensaje=mensaje, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)
    
    # ==================== ESTO ES LO QUE FALTABA ====================
    # GET request o formulario inválido
    fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
    return render_template('formularios/inspeccion_ge.html', form=form, usuario=session['nombre'], fecha=fecha_actual, fecha_iso=fecha_iso, dia_turno=dia_turno, turno=turno, estado_turno=estado_turno)

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
    
    # Obtener inspecciones COW
    if usuario_actual.rol == 'supervisor':
        cow_inspecciones = InspeccionCOW.query.order_by(InspeccionCOW.fecha_registro.desc()).all()
    else:
        cow_inspecciones = InspeccionCOW.query.filter_by(usuario_id=usuario_actual.id).order_by(InspeccionCOW.fecha_registro.desc()).all()
    
    # Obtener inspecciones GE
    if usuario_actual.rol == 'supervisor':
        ge_inspecciones = InspeccionGE.query.order_by(InspeccionGE.fecha_registro.desc()).all()
    else:
        ge_inspecciones = InspeccionGE.query.filter_by(usuario_id=usuario_actual.id).order_by(InspeccionGE.fecha_registro.desc()).all()
    
    # Unificar y agregar tipo
    inspecciones_unificadas = []
    for ins in cow_inspecciones:
        inspecciones_unificadas.append({
            'id': ins.id,
            'tipo': 'cow',
            'fecha': ins.fecha,
            'dia_turno': ins.dia_turno,
            'sitio': ins.sitio_ref.nombre_sitio if ins.sitio_ref else ins.nombre_sitio,
            'responsable': ins.responsable,
            'estado': ins.estado
        })
    
    for ins in ge_inspecciones:
        inspecciones_unificadas.append({
            'id': ins.id,
            'tipo': 'ge',
            'fecha': ins.fecha,
            'dia_turno': ins.dia_turno,
            'sitio': ins.nombre_ge,  # GE usa nombre_ge
            'responsable': ins.responsable,
            'estado': ins.estado
        })
    
    # Ordenar por fecha descendente
    inspecciones_unificadas.sort(key=lambda x: x['fecha'], reverse=True)
    
    return render_template('ver_informes.html', usuario=session['nombre'], rol=session['rol'], inspecciones=inspecciones_unificadas)

@app.route('/ver_informe/<int:id>')
def ver_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'cow')
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    if tipo == 'cow':
        inspeccion = InspeccionCOW.query.get_or_404(id)
        template = 'ver_informe.html'
    elif tipo == 'ge':
        inspeccion = InspeccionGE.query.get_or_404(id)
        template = 'ver_informe_ge.html'
    else:
        return "Tipo de informe no válido", 400
    
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para ver este informe", 403
    
    return render_template(template, inspeccion=inspeccion, usuario=session['nombre'], rol=session['rol'], tipo=tipo)

@app.route('/aprobar_informe/<int:id>')
def aprobar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    if usuario_actual.rol != 'supervisor':
        return "Acceso denegado", 403
    
    tipo = request.args.get('tipo', 'cow')
    if tipo == 'cow':
        inspeccion = InspeccionCOW.query.get_or_404(id)
    elif tipo == 'ge':
        inspeccion = InspeccionGE.query.get_or_404(id)
    else:
        return "Tipo de informe no válido", 400

    inspeccion.estado = 'aprobado'
    db.session.commit()
    
    return redirect(url_for('ver_informes'))

@app.route('/rechazar_informe/<int:id>', methods=['GET', 'POST'])
def rechazar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'cow')
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    if usuario_actual.rol != 'supervisor':
        return "Acceso denegado", 403
    
    if tipo == 'cow':
        inspeccion = InspeccionCOW.query.get_or_404(id)
    elif tipo == 'ge':
        inspeccion = InspeccionGE.query.get_or_404(id)
    else:
        return "Tipo de informe no válido", 400
    
    if request.method == 'POST':
        motivo = request.form.get('motivo_rechazo', '')
        inspeccion.estado = 'rechazado'
        inspeccion.motivo_rechazo = motivo
        db.session.commit()
        return redirect(url_for('ver_informes'))
    
    return render_template('rechazar_informe.html', inspeccion=inspeccion)

@app.route('/editar_informe/<int:id>', methods=['GET', 'POST'])
def editar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'cow')
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    # Obtener la inspección y el formulario según el tipo
    if tipo == 'cow':
        inspeccion = InspeccionCOW.query.get_or_404(id)
        form = InspeccionCOWForm()
        template = 'formularios/inspeccion_cow.html'
        # Cargar opciones de sitios
        sitios = Sitio.query.filter_by(activo=True).all()
        form.nombre_sitio.choices = [(str(s.id), s.nombre_sitio) for s in sitios]
    elif tipo == 'ge':
        inspeccion = InspeccionGE.query.get_or_404(id)
        form = InspeccionGEForm()
        template = 'formularios/inspeccion_ge.html'
    else:
        return "Tipo de informe no válido", 400
    
    # Verificar permiso
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para editar este informe", 403
    
    if request.method == 'POST' and form.validate_on_submit():
        # Obtener fecha
        fecha_seleccionada = request.form.get('fecha')
        if fecha_seleccionada:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno(fecha_seleccionada)
        else:
            fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
        
        # Actualizar campos comunes
        inspeccion.fecha = fecha_actual
        inspeccion.dia_turno = dia_turno
        inspeccion.responsable = form.responsable.data
        inspeccion.horometro = form.horometro.data
        inspeccion.hora_inicio = form.hora_inicio.data
        inspeccion.hora_termino = form.hora_termino.data
        
        if tipo == 'cow':
            # ==================== CAMPOS COW ====================
            inspeccion.sitio_id = int(form.nombre_sitio.data)
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
            
            # Procesar fotos COW
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
            
            # Fotos Mejoras (4)
            for i in range(1, 5):
                campo_foto = f'foto_mejora_{i}'
                campo_desc = f'desc_mejora_{i}'
                desc = request.form.get(campo_desc, '')
                setattr(inspeccion, f'descripcion_mejora_{i}', desc)
                if campo_foto in request.files:
                    file = request.files[campo_foto]
                    if file and file.filename:
                        filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_edit_mejora_{i}.jpg")
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        setattr(inspeccion, f'foto_mejora_{i}', filename)
        
        elif tipo == 'ge':
            # ==================== CAMPOS GE ====================
            inspeccion.nombre_ge = form.nombre_ge.data
            inspeccion.tipo_ge = form.tipo_ge.data
            inspeccion.potencia_continua = form.potencia_continua.data
            inspeccion.cantidad_arranques = form.cantidad_arranques.data
            inspeccion.horas_funcionamiento = form.horas_funcionamiento.data
            inspeccion.nivel_aceite = form.nivel_aceite.data
            inspeccion.nivel_combustible = form.nivel_combustible.data
            inspeccion.nivel_refrigerante = form.nivel_refrigerante.data
            inspeccion.proxima_mantencion = form.proxima_mantencion.data
            inspeccion.estado_carcasa = form.estado_carcasa.data
            inspeccion.limpieza_ge_interior = form.limpieza_ge_interior.data
            inspeccion.limpieza_radiador = form.limpieza_radiador.data
            inspeccion.visor_combustible = form.visor_combustible.data
            inspeccion.arranque_automatico = form.arranque_automatico.data
            inspeccion.limpieza_interior = form.limpieza_interior.data
            inspeccion.limpieza_exterior = form.limpieza_exterior.data
            inspeccion.cable_5p_4p = form.cable_5p_4p.data
            inspeccion.observaciones = form.observaciones.data
            
            # Estado Breaker y Baterías
            inspeccion.estado_pantalla = form.estado_pantalla.data
            inspeccion.estado_parada_emergencia = form.estado_parada_emergencia.data
            inspeccion.estado_corta_corriente = form.estado_corta_corriente.data
            inspeccion.estado_selector = form.estado_selector.data
            inspeccion.estado_bornes_bateria = form.estado_bornes_bateria.data
            inspeccion.estado_ramal_cables = form.estado_ramal_cables.data
            inspeccion.estado_enchufe = form.estado_enchufe.data
            inspeccion.estado_cebador = form.estado_cebador.data
            inspeccion.estado_mangueras = form.estado_mangueras.data
            inspeccion.estado_alarmas = form.estado_alarmas.data
            inspeccion.estado_extintor = form.estado_extintor.data
            inspeccion.estado_puertas = form.estado_puertas.data
            inspeccion.estado_baterias = form.estado_baterias.data
            inspeccion.estado_ventilador = form.estado_ventilador.data
            inspeccion.observaciones_breaker = form.observaciones_breaker.data
            
            # Estructuras
            inspeccion.limpieza_general = form.limpieza_general.data
            inspeccion.estado_chasis = form.estado_chasis.data
            inspeccion.cantidad_cunas = form.cantidad_cunas.data
            inspeccion.checkpoints = form.checkpoints.data
            inspeccion.presion_neumaticos = form.presion_neumaticos.data
            inspeccion.estado_jaula = form.estado_jaula.data
            inspeccion.estado_candados = form.estado_candados.data
            inspeccion.nivelacion_carro = form.nivelacion_carro.data
            inspeccion.patas_posicionamiento = form.patas_posicionamiento.data
            inspeccion.manivelas_izajes = form.manivelas_izajes.data
            inspeccion.observaciones_estructuras = form.observaciones_estructuras.data
            
            # Procesar fotos GE
            # Fotos GE (3)
            for i in range(1, 4):
                campo_foto = f'foto_{i}'
                if campo_foto in request.files:
                    file = request.files[campo_foto]
                    if file and file.filename:
                        filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_ge_edit_{i}.jpg")
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        setattr(inspeccion, f'foto_{i}', filename)
            
            # Fotos Breaker (3)
            for i in range(1, 4):
                campo_foto = f'foto_breaker_{i}'
                if campo_foto in request.files:
                    file = request.files[campo_foto]
                    if file and file.filename:
                        filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_breaker_edit_{i}.jpg")
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        setattr(inspeccion, f'foto_breaker_{i}', filename)
            
            # Fotos Estructuras (3)
            for i in range(1, 4):
                campo_foto = f'foto_estructura_{i}'
                if campo_foto in request.files:
                    file = request.files[campo_foto]
                    if file and file.filename:
                        filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_estructura_edit_{i}.jpg")
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        setattr(inspeccion, f'foto_estructura_{i}', filename)
            
            # Fotos Levantamiento (8)
            for i in range(1, 9):
                campo_foto = f'foto_lev_{i}'
                if campo_foto in request.files:
                    file = request.files[campo_foto]
                    if file and file.filename:
                        filename = secure_filename(f"{session['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_lev_edit_{i}.jpg")
                        filepath = os.path.join('static/uploads', filename)
                        file.save(filepath)
                        setattr(inspeccion, f'foto_lev_{i}', filename)
        
        # Cambiar estado a pendiente después de editar
        inspeccion.estado = 'pendiente'
        db.session.commit()
        
        return redirect(url_for('ver_informes'))
    
    # GET request - Cargar datos existentes en el formulario
    if request.method == 'GET':
        form.responsable.data = inspeccion.responsable
        form.horometro.data = inspeccion.horometro
        form.hora_inicio.data = inspeccion.hora_inicio
        form.hora_termino.data = inspeccion.hora_termino
        
        if tipo == 'cow':
            form.nombre_sitio.data = str(inspeccion.sitio_id) if inspeccion.sitio_id else ''
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
        
        elif tipo == 'ge':
            form.nombre_ge.data = inspeccion.nombre_ge
            form.tipo_ge.data = inspeccion.tipo_ge
            form.potencia_continua.data = inspeccion.potencia_continua
            form.cantidad_arranques.data = inspeccion.cantidad_arranques
            form.horas_funcionamiento.data = inspeccion.horas_funcionamiento
            form.nivel_aceite.data = inspeccion.nivel_aceite
            form.nivel_combustible.data = inspeccion.nivel_combustible
            form.nivel_refrigerante.data = inspeccion.nivel_refrigerante
            form.proxima_mantencion.data = inspeccion.proxima_mantencion
            form.estado_carcasa.data = inspeccion.estado_carcasa
            form.limpieza_ge_interior.data = inspeccion.limpieza_ge_interior
            form.limpieza_radiador.data = inspeccion.limpieza_radiador
            form.visor_combustible.data = inspeccion.visor_combustible
            form.arranque_automatico.data = inspeccion.arranque_automatico
            form.limpieza_interior.data = inspeccion.limpieza_interior
            form.limpieza_exterior.data = inspeccion.limpieza_exterior
            form.cable_5p_4p.data = inspeccion.cable_5p_4p
            form.observaciones.data = inspeccion.observaciones
            form.estado_pantalla.data = inspeccion.estado_pantalla
            form.estado_parada_emergencia.data = inspeccion.estado_parada_emergencia
            form.estado_corta_corriente.data = inspeccion.estado_corta_corriente
            form.estado_selector.data = inspeccion.estado_selector
            form.estado_bornes_bateria.data = inspeccion.estado_bornes_bateria
            form.estado_ramal_cables.data = inspeccion.estado_ramal_cables
            form.estado_enchufe.data = inspeccion.estado_enchufe
            form.estado_cebador.data = inspeccion.estado_cebador
            form.estado_mangueras.data = inspeccion.estado_mangueras
            form.estado_alarmas.data = inspeccion.estado_alarmas
            form.estado_extintor.data = inspeccion.estado_extintor
            form.estado_puertas.data = inspeccion.estado_puertas
            form.estado_baterias.data = inspeccion.estado_baterias
            form.estado_ventilador.data = inspeccion.estado_ventilador
            form.observaciones_breaker.data = inspeccion.observaciones_breaker
            form.limpieza_general.data = inspeccion.limpieza_general
            form.estado_chasis.data = inspeccion.estado_chasis
            form.cantidad_cunas.data = inspeccion.cantidad_cunas
            form.checkpoints.data = inspeccion.checkpoints
            form.presion_neumaticos.data = inspeccion.presion_neumaticos
            form.estado_jaula.data = inspeccion.estado_jaula
            form.estado_candados.data = inspeccion.estado_candados
            form.nivelacion_carro.data = inspeccion.nivelacion_carro
            form.patas_posicionamiento.data = inspeccion.patas_posicionamiento
            form.manivelas_izajes.data = inspeccion.manivelas_izajes
            form.observaciones_estructuras.data = inspeccion.observaciones_estructuras
    
    fecha_actual, fecha_iso, dia_turno, turno, estado_turno = calcular_fecha_turno()
    return render_template(template, form=form, usuario=session['nombre'], 
                      fecha=fecha_actual, fecha_iso=fecha_iso, 
                      dia_turno=dia_turno, turno=turno, 
                      estado_turno=estado_turno, editando=True, 
                      id_inspeccion=id, inspeccion=inspeccion,
                      inspeccion_ge=inspeccion)

@app.route('/borrar_informe/<int:id>')
def borrar_informe(id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    tipo = request.args.get('tipo', 'cow')
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    if tipo == 'cow':
        inspeccion = InspeccionCOW.query.get_or_404(id)
    elif tipo == 'ge':
        inspeccion = InspeccionGE.query.get_or_404(id)
    else:
        return "Tipo de informe no válido", 400
    
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para borrar este informe", 403
    
    db.session.delete(inspeccion)
    db.session.commit()
    
    return redirect(url_for('ver_informes'))

# ==================== API REST ====================

# 1. Obtener todas las inspecciones (GET)
@app.route('/api/inspecciones', methods=['GET'])
def api_get_inspecciones():
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    if usuario_actual.rol == 'supervisor':
        inspecciones = InspeccionCOW.query.all()
    else:
        inspecciones = InspeccionCOW.query.filter_by(usuario_id=usuario_actual.id).all()
    
    resultado = []
    for ins in inspecciones:
        # Obtener nombre del sitio desde la relación
        sitio = Sitio.query.get(ins.sitio_id) if ins.sitio_id else None
        nombre_sitio = sitio.nombre_sitio if sitio else 'Desconocido'
        
        resultado.append({
            'id': ins.id,
            'fecha': ins.fecha,
            'sitio': nombre_sitio,
            'responsable': ins.responsable,
            'estado': ins.estado
        })
    
    return jsonify(resultado)

# 2. Obtener una inspección específica por ID (GET)
@app.route('/api/inspecciones/<int:id>', methods=['GET'])
def api_get_inspeccion(id):
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    inspeccion = InspeccionCOW.query.get_or_404(id)
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return jsonify({'error': 'No tienes permiso para ver esta inspección'}), 403
    
    # Obtener nombre del sitio
    sitio = Sitio.query.get(inspeccion.sitio_id) if inspeccion.sitio_id else None
    nombre_sitio = sitio.nombre_sitio if sitio else 'Desconocido'
    
    # Obtener fotos de la inspección
    fotos = []
    for foto in inspeccion.fotografias:
        fotos.append({
            'seccion': foto.seccion,
            'punto_numero': foto.punto_numero,
            'ruta': foto.ruta_archivo
        })
    
    # Obtener mejoras
    mejoras = []
    for mejora in inspeccion.mejoras:
        mejoras.append({
            'numero': mejora.numero,
            'descripcion': mejora.descripcion,
            'ruta_foto': mejora.ruta_foto
        })
    
    resultado = {
        'id': inspeccion.id,
        'fecha': inspeccion.fecha,
        'dia_turno': inspeccion.dia_turno,
        'sitio': nombre_sitio,
        'responsable': inspeccion.responsable,
        'horometro': inspeccion.horometro,
        'hora_inicio': inspeccion.hora_inicio,
        'hora_termino': inspeccion.hora_termino,
        'horas_funcionamiento': inspeccion.horas_funcionamiento,
        'cantidad_arranques': inspeccion.cantidad_arranques,
        'nivel_aceite': inspeccion.nivel_aceite,
        'nivel_combustible': inspeccion.nivel_combustible,
        'observaciones_ge': inspeccion.observaciones_ge,
        'estado': inspeccion.estado,
        'fotos': fotos,
        'mejoras': mejoras
    }
    
    return jsonify(resultado)

# 3. Obtener todos los sitios (GET)
@app.route('/api/sitios', methods=['GET'])
def api_get_sitios():
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    sitios = Sitio.query.filter_by(activo=True).all()
    resultado = [{'id': s.id, 'nombre': s.nombre_sitio, 'area': s.area, 'tipo': s.tipo} for s in sitios]
    
    return jsonify(resultado)

# 4. Obtener estadísticas (solo supervisor)
@app.route('/api/estadisticas', methods=['GET'])
def api_get_estadisticas():
    if 'username' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    if usuario_actual.rol != 'supervisor':
        return jsonify({'error': 'Solo supervisores pueden ver estadísticas'}), 403
    
    total = InspeccionCOW.query.count()
    pendientes = InspeccionCOW.query.filter_by(estado='pendiente').count()
    aprobados = InspeccionCOW.query.filter_by(estado='aprobado').count()
    rechazados = InspeccionCOW.query.filter_by(estado='rechazado').count()
    
    return jsonify({
        'total': total,
        'pendientes': pendientes,
        'aprobados': aprobados,
        'rechazados': rechazados
    })

@app.route('/generar_pdf/<int:id>')
@app.route('/generar_pdf/<int:id>/<tipo>')
def generar_pdf(id, tipo=None):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Detectar tipo de inspección
    if tipo is None:
        inspeccion_cow = InspeccionCOW.query.get(id)
        if inspeccion_cow:
            tipo = 'cow'
            inspeccion = inspeccion_cow
        else:
            inspeccion_ge = InspeccionGE.query.get(id)
            if inspeccion_ge:
                tipo = 'ge'
                inspeccion = inspeccion_ge
            else:
                return "Inspección no encontrada", 404
    else:
        if tipo == 'cow':
            inspeccion = InspeccionCOW.query.get_or_404(id)
        elif tipo == 'ge':
            inspeccion = InspeccionGE.query.get_or_404(id)
        else:
            return "Tipo de inspección no válido", 400
    
    usuario_actual = Usuario.query.filter_by(username=session['username']).first()
    
    if usuario_actual.rol != 'supervisor' and inspeccion.usuario_id != usuario_actual.id:
        return "No tienes permiso para generar este PDF", 403
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           topMargin=0.7*inch, bottomMargin=0.7*inch,
                           leftMargin=0.7*inch, rightMargin=0.7*inch)
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle('TituloStyle', parent=styles['Heading1'],
                                   alignment=TA_CENTER, fontSize=18, 
                                   textColor=colors.HexColor('#0033a0'),
                                   spaceAfter=20, fontName='Helvetica-Bold')
    
    subtitulo_style = ParagraphStyle('SubtituloStyle', parent=styles['Heading2'],
                                      fontSize=14, textColor=colors.HexColor('#0033a0'),
                                      spaceBefore=15, spaceAfter=10, fontName='Helvetica-Bold')
    
    normal_style = styles['Normal']
    cell_style = ParagraphStyle('CellStyle', parent=normal_style, fontSize=9)
    titulo_tabla_style = ParagraphStyle('TituloTablaStyle', parent=normal_style,
                                         alignment=TA_CENTER, fontSize=11, 
                                         fontName='Helvetica-Bold')
    
    elementos = []
    
    # ==================== SI ES COW ====================
    if tipo == 'cow':
        # ==================== ENCABEZADO ====================
        try:
            logo_nokia = Image('static/img/nokia_logo.png', width=1.5*inch, height=0.5*inch)
        except:
            logo_nokia = Paragraph("", normal_style)
        
        titulo_encabezado = Paragraph("INSPECCIÓN DIARIA COW", 
                                       ParagraphStyle('EncabezadoStyle', parent=normal_style,
                                                     alignment=TA_CENTER, fontSize=14, 
                                                     textColor=colors.HexColor("#000000"),
                                                     fontName='Helvetica-Bold'))
        
        try:
            logo_sonda = Image('static/img/sonda_logo.png', width=1.5*inch, height=0.5*inch)
        except:
            logo_sonda = Paragraph("", normal_style)
        
        encabezado_tabla = Table([[logo_nokia, titulo_encabezado, logo_sonda]], 
                                  colWidths=[2.0*inch, 3.0*inch, 2.0*inch])
        encabezado_tabla.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        elementos.append(encabezado_tabla)
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== DATOS PRINCIPALES ====================
        datos_principales = [
            [Paragraph("<b>DATOS PRINCIPALES</b>", titulo_tabla_style), ""],
            [Paragraph(f"<b>Responsable:</b> {inspeccion.responsable}", cell_style),
             Paragraph(f"<b>Fecha:</b> {inspeccion.fecha} (Día {inspeccion.dia_turno})", cell_style)],
            [Paragraph(f"<b>Nombre del Sitio:</b> {inspeccion.sitio_ref.nombre_sitio if inspeccion.sitio_ref else 'N/A'}", cell_style),
             Paragraph(f"<b>Hora Inicio:</b> {inspeccion.hora_inicio}", cell_style)],
            [Paragraph(f"<b>Horómetro:</b> {inspeccion.horometro}", cell_style),
             Paragraph(f"<b>Hora Término:</b> {inspeccion.hora_termino}", cell_style)],
        ]
        
        tabla_principales = Table(datos_principales, colWidths=[3.5*inch, 3.5*inch])
        tabla_principales.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
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
        
        # ==================== GE (solo si no es Light) ====================
        nombre_sitio_str = inspeccion.sitio_ref.nombre_sitio if inspeccion.sitio_ref else ''
        es_cow_light = 'Light' in nombre_sitio_str
        
        if not es_cow_light:
            titulo_ge = Paragraph("Grupo Electrógeno Cummins y Estanque de Combustible", 
                                  ParagraphStyle('TituloGEStyle', parent=normal_style,
                                                alignment=TA_CENTER, fontSize=12,
                                                textColor=colors.HexColor("#000000"),
                                                fontName='Helvetica-Bold'))
            
            datos_ge = [
                [titulo_ge, "", "", ""],
                [Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style), 
                 Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
                [Paragraph("<b>Horas de Funcionamiento</b>", cell_style), 
                 Paragraph(str(inspeccion.horas_funcionamiento or '-'), cell_style),
                 Paragraph("<b>Limpieza GE Interior</b>", cell_style),
                 Paragraph("X" if inspeccion.limpieza_ge_interior == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.limpieza_ge_interior == 'NOK' else "", cell_style)],
                [Paragraph("<b>Cantidad de Arranques</b>", cell_style), 
                 Paragraph(str(inspeccion.cantidad_arranques or '-'), cell_style),
                 Paragraph("<b>Limpieza Radiador</b>", cell_style),
                 Paragraph("X" if inspeccion.limpieza_radiador == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.limpieza_radiador == 'NOK' else "", cell_style)],
                [Paragraph("<b>Nivel de Aceite</b>", cell_style), 
                 Paragraph(inspeccion.nivel_aceite or '-', cell_style),
                 Paragraph("<b>Sistema Combustible</b>", cell_style),
                 Paragraph("X" if inspeccion.sistema_combustible == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.sistema_combustible == 'NOK' else "", cell_style)],
                [Paragraph("<b>Nivel de Combustible</b>", cell_style), 
                 Paragraph(inspeccion.nivel_combustible or '-', cell_style),
                 Paragraph("<b>Arranque Automático</b>", cell_style),
                 Paragraph("X" if inspeccion.arranque_automatico == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.arranque_automatico == 'NOK' else "", cell_style)],
                [Paragraph("<b>Nivel de Refrigerante</b>", cell_style), 
                 Paragraph(inspeccion.nivel_refrigerante or '-', cell_style),
                 Paragraph("<b>Limpieza Interior</b>", cell_style),
                 Paragraph("X" if inspeccion.limpieza_interior == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.limpieza_interior == 'NOK' else "", cell_style)],
                [Paragraph("<b>Próxima Mantención</b>", cell_style), 
                 Paragraph(str(inspeccion.proxima_mantencion or '-'), cell_style),
                 Paragraph("<b>Limpieza Exterior</b>", cell_style),
                 Paragraph("X" if inspeccion.limpieza_exterior == 'OK' else "", cell_style),
                 Paragraph("X" if inspeccion.limpieza_exterior == 'NOK' else "", cell_style)],
            ]
            
            tabla_ge = Table(datos_ge, colWidths=[2.8*inch, 0.9*inch, 2.3*inch, 0.5*inch, 0.5*inch])
            tabla_ge.setStyle(TableStyle([
                ('SPAN', (0,0), (4,0)),
                ('SPAN', (0,1), (2,1)),
                ('ALIGN', (0,0), (-1,0), 'CENTER'),
                ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
                ('ALIGN', (0,2), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('ALIGN', (0,2), (0,-1), 'LEFT'),
                ('ALIGN', (2,2), (2,-1), 'LEFT'),
            ]))
            elementos.append(tabla_ge)
            
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
            
            texto_observaciones = inspeccion.observaciones_ge or 'Sin observaciones'
            datos_obs_fotos = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones}", cell_style)]]
            
            fotos_ge = [('foto_1', 'Foto 1'), ('foto_2', 'Foto 2'), ('foto_3', 'Foto 3')]
            for campo, titulo in fotos_ge:
                foto_nombre = getattr(inspeccion, campo, None)
                if foto_nombre:
                    ruta_foto = os.path.join('static/uploads', foto_nombre)
                    if os.path.exists(ruta_foto):
                        try:
                            img = Image(ruta_foto, width=5*inch, height=3*inch)
                            contenido_tabla = Table([
                                [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                                [img]
                            ], colWidths=[5.5*inch])
                            contenido_tabla.setStyle(TableStyle([
                                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                                ('TOPPADDING', (0,0), (-1,-1), 2),
                                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                            ]))
                            datos_obs_fotos.append([contenido_tabla])
                        except:
                            pass
            
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
        
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== RACK ENERGÍA ====================
        titulo_rack = Paragraph("Rack Energía, Telecom y Baterías", 
                                ParagraphStyle('TituloRackStyle', parent=normal_style,
                                              alignment=TA_CENTER, fontSize=12,
                                              textColor=colors.HexColor("#000000"),
                                              fontName='Helvetica-Bold'))
        
        datos_rack = [
            [titulo_rack, "", "", "", "", ""],
            [Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style),
             Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
            [Paragraph("<b>Limpieza Rack Energía</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_energia == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_energia == 'NOK' else "", cell_style),
             Paragraph("<b>Limpieza Rack Telecom</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_telecom == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_telecom == 'NOK' else "", cell_style)],
            [Paragraph("<b>Estado Planta Vertiv</b>", cell_style),
             Paragraph("X" if inspeccion.estado_planta_vertiv == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_planta_vertiv == 'NOK' else "", cell_style),
             Paragraph("<b>Estado Air Scale</b>", cell_style),
             Paragraph("X" if inspeccion.estado_air_scale == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_air_scale == 'NOK' else "", cell_style)],
            [Paragraph("<b>Rectificador N°1</b>", cell_style),
             Paragraph("X" if inspeccion.rectificador_n1 == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.rectificador_n1 == 'NOK' else "", cell_style),
             Paragraph("<b>Estado de Alarmas</b>", cell_style),
             Paragraph("X" if inspeccion.estado_alarmas == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_alarmas == 'NOK' else "", cell_style)],
            [Paragraph("<b>Rectificador N°2</b>", cell_style),
             Paragraph("X" if inspeccion.rectificador_n2 == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.rectificador_n2 == 'NOK' else "", cell_style),
             Paragraph("<b>Estado 7250-IXR</b>", cell_style),
             Paragraph("X" if inspeccion.estado_7250_ixr == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_7250_ixr == 'NOK' else "", cell_style)],
            [Paragraph("<b>Rectificador N°3</b>", cell_style),
             Paragraph("X" if inspeccion.rectificador_n3 == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.rectificador_n3 == 'NOK' else "", cell_style),
             Paragraph("<b>Estado FPFH</b>", cell_style),
             Paragraph("X" if inspeccion.estado_fpfh == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_fpfh == 'NOK' else "", cell_style)],
            [Paragraph("<b>Conversor Solar N°1</b>", cell_style),
             Paragraph("X" if inspeccion.conversor_solar_n1 == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.conversor_solar_n1 == 'NOK' else "", cell_style),
             Paragraph("<b>Limpieza Rack Baterías</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_baterias == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_rack_baterias == 'NOK' else "", cell_style)],
            [Paragraph("<b>Conversor Solar N°2</b>", cell_style),
             Paragraph("X" if inspeccion.conversor_solar_n2 == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.conversor_solar_n2 == 'NOK' else "", cell_style),
             Paragraph("<b>Estado Baterías</b>", cell_style),
             Paragraph("X" if inspeccion.estado_baterias == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_baterias == 'NOK' else "", cell_style)],
            [Paragraph("<b>Estado Inversor</b>", cell_style),
             Paragraph("X" if inspeccion.estado_inversor == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_inversor == 'NOK' else "", cell_style),
             Paragraph("<b>Estado Ventiladores</b>", cell_style),
             Paragraph("X" if inspeccion.estado_ventiladores == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_ventiladores == 'NOK' else "", cell_style)],
        ]
        
        tabla_rack = Table(datos_rack, colWidths=[2.7*inch, 0.5*inch, 0.5*inch, 2.3*inch, 0.5*inch, 0.5*inch])
        tabla_rack.setStyle(TableStyle([
            ('SPAN', (0,0), (5,0)),
            ('SPAN', (0,1), (0,1)),
            ('SPAN', (3,1), (3,1)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('ALIGN', (1,2), (5,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,2), (0,-1), 'LEFT'),
            ('ALIGN', (3,2), (3,-1), 'LEFT'),
        ]))
        elementos.append(tabla_rack)
        
        # Observaciones y fotos Rack
        texto_observaciones_rack = inspeccion.observaciones_rack or 'Sin observaciones'
        datos_obs_fotos_rack = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones_rack}", cell_style)]]
        
        fotos_rack_lista = [('foto_rack_1', 'Foto Rack 1'), ('foto_rack_2', 'Foto Rack 2'), ('foto_rack_3', 'Foto Rack 3')]
        for campo, titulo in fotos_rack_lista:
            foto_nombre = getattr(inspeccion, campo, None)
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = Image(ruta_foto, width=5*inch, height=3*inch)
                        contenido_tabla = Table([
                            [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                            [img]
                        ], colWidths=[5.5*inch])
                        contenido_tabla.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        datos_obs_fotos_rack.append([contenido_tabla])
                    except:
                        pass
        
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
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== ESTRUCTURAS ====================
        titulo_estructuras = Paragraph("Estructuras, Paneles Solares, Piolas de Viento, Neumáticos y otros", 
                                        ParagraphStyle('TituloEstructurasStyle', parent=normal_style,
                                                      alignment=TA_CENTER, fontSize=12,
                                                      textColor=colors.HexColor("#000000"),
                                                      fontName='Helvetica-Bold'))
        
        datos_estructuras = [
            [titulo_estructuras, "", "", "", "", ""],
            [Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style),
             Paragraph("", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
            [Paragraph("<b>Limpieza de Paneles</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_paneles == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_paneles == 'NOK' else "", cell_style),
             Paragraph("<b>Estado de Torre</b>", cell_style),
             Paragraph("X" if inspeccion.estado_torre == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_torre == 'NOK' else "", cell_style)],
            [Paragraph("<b>Estructura de P. Solares</b>", cell_style),
             Paragraph("X" if inspeccion.estructura_paneles == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estructura_paneles == 'NOK' else "", cell_style),
             Paragraph("<b>Estado Piolas de Viento</b>", cell_style),
             Paragraph("X" if inspeccion.estado_piolas_viento == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.estado_piolas_viento == 'NOK' else "", cell_style)],
            [Paragraph("<b>Cantidad de Cuñas</b>", cell_style),
             Paragraph(str(inspeccion.cantidad_cunas or '-'), cell_style),
             Paragraph("", cell_style),
             Paragraph("<b>Nivelación del Carro</b>", cell_style),
             Paragraph("X" if inspeccion.nivelacion_carro == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.nivelacion_carro == 'NOK' else "", cell_style)],
            [Paragraph("<b>Checkpoints</b>", cell_style),
             Paragraph("X" if inspeccion.checkpoints == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.checkpoints == 'NOK' else "", cell_style),
             Paragraph("<b>Gatas de Posicionamiento</b>", cell_style),
             Paragraph("X" if inspeccion.gatas_posicionamiento == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.gatas_posicionamiento == 'NOK' else "", cell_style)],
            [Paragraph("<b>Presión de Neumáticos</b>", cell_style),
             Paragraph("X" if inspeccion.presion_neumaticos == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.presion_neumaticos == 'NOK' else "", cell_style),
             Paragraph("<b>Manivelas Izaje de Gatas</b>", cell_style),
             Paragraph("X" if inspeccion.manivelas_izaje == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.manivelas_izaje == 'NOK' else "", cell_style)],
        ]
        
        tabla_estructuras = Table(datos_estructuras, colWidths=[2.7*inch, 0.5*inch, 0.5*inch, 2.3*inch, 0.5*inch, 0.5*inch])
        tabla_estructuras.setStyle(TableStyle([
            ('SPAN', (0,0), (5,0)),
            ('SPAN', (0,1), (0,1)),
            ('SPAN', (3,1), (3,1)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('ALIGN', (1,2), (5,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,2), (0,-1), 'LEFT'),
            ('ALIGN', (3,2), (3,-1), 'LEFT'),
        ]))
        elementos.append(tabla_estructuras)
        
        texto_observaciones_estructuras = inspeccion.observaciones_estructuras or 'Sin observaciones'
        datos_obs_fotos_estructuras = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones_estructuras}", cell_style)]]
        
        fotos_estructuras_lista = [('foto_estructuras_1', 'Foto Estructura 1'), 
                                    ('foto_estructuras_2', 'Foto Estructura 2'), 
                                    ('foto_estructuras_3', 'Foto Estructura 3')]
        for campo, titulo in fotos_estructuras_lista:
            foto_nombre = getattr(inspeccion, campo, None)
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = Image(ruta_foto, width=5*inch, height=3*inch)
                        contenido_tabla = Table([
                            [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                            [img]
                        ], colWidths=[5.5*inch])
                        contenido_tabla.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        datos_obs_fotos_estructuras.append([contenido_tabla])
                    except:
                        pass
        
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
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== LEVANTAMIENTO DE FOTOGRAFÍAS (33 PUNTOS) ====================
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
            if not foto_nombre:
                return None
            ruta_foto = os.path.join('static/uploads', foto_nombre)
            if not os.path.exists(ruta_foto):
                return None
            try:
                img = Image(ruta_foto, width=5*inch, height=3*inch)
                contenido_celda = [Paragraph(f"<b>{titulo}</b>", cell_style), img]
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
        
        for num, titulo, campo_foto in puntos_fotos:
            foto_nombre = getattr(inspeccion, campo_foto, None)
            tabla = crear_tabla_foto(titulo, foto_nombre)
            if tabla:
                elementos.append(tabla)
        
        # ==================== MEJORAS ====================
        mejoras_lista = [
            (inspeccion.descripcion_mejora_1, inspeccion.foto_mejora_1),
            (inspeccion.descripcion_mejora_2, inspeccion.foto_mejora_2),
            (inspeccion.descripcion_mejora_3, inspeccion.foto_mejora_3),
            (inspeccion.descripcion_mejora_4, inspeccion.foto_mejora_4),
        ]
        
        hay_mejoras = any(desc or foto for desc, foto in mejoras_lista)
        
        if hay_mejoras:
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
                contenido_celda = []
                if descripcion and descripcion.strip():
                    contenido_celda.append(Paragraph(f"<b>Mejora:</b> {descripcion}", cell_style))
                else:
                    contenido_celda.append(Paragraph("<b>Mejora:</b> (Sin descripción)", cell_style))
                
                if foto_nombre:
                    ruta_foto = os.path.join('static/uploads', foto_nombre)
                    if os.path.exists(ruta_foto):
                        try:
                            img = Image(ruta_foto, width=5*inch, height=3*inch)
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
            
            for desc, foto in mejoras_lista:
                if desc or foto:
                    elementos.append(crear_tabla_mejora(desc or '', foto))
    
        # ==================== SI ES GE AUXILIAR ====================
    else:  # tipo == 'ge'
        # ==================== ENCABEZADO ====================
        try:
            logo_nokia = Image('static/img/nokia_logo.png', width=1.5*inch, height=0.5*inch)
        except:
            logo_nokia = Paragraph("", normal_style)
        
        titulo_encabezado = Paragraph("INSPECCIÓN GE AUXILIAR", 
                                       ParagraphStyle('EncabezadoStyle', parent=normal_style,
                                                     alignment=TA_CENTER, fontSize=14, 
                                                     textColor=colors.HexColor("#000000"),
                                                     fontName='Helvetica-Bold'))
        
        try:
            logo_sonda = Image('static/img/sonda_logo.png', width=1.5*inch, height=0.5*inch)
        except:
            logo_sonda = Paragraph("", normal_style)
        
        encabezado_tabla = Table([[logo_nokia, titulo_encabezado, logo_sonda]], 
                                  colWidths=[2.0*inch, 3.0*inch, 2.0*inch])
        encabezado_tabla.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]))
        elementos.append(encabezado_tabla)
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== DATOS GENERALES ====================
        datos_principales = [
            [Paragraph("<b>DATOS GENERALES</b>", titulo_tabla_style), ""],
            [Paragraph(f"<b>Responsable:</b> {inspeccion.responsable}", cell_style),
             Paragraph(f"<b>Fecha:</b> {inspeccion.fecha} (Día {inspeccion.dia_turno})", cell_style)],
            [Paragraph(f"<b>Nombre GE Auxiliar:</b> {inspeccion.nombre_ge}", cell_style),
             Paragraph(f"<b>Hora Inicio:</b> {inspeccion.hora_inicio}", cell_style)],
            [Paragraph(f"<b>Horómetro:</b> {inspeccion.horometro}", cell_style),
             Paragraph(f"<b>Hora Término:</b> {inspeccion.hora_termino}", cell_style)],
            [Paragraph(f"<b>Tipo GE:</b> {inspeccion.tipo_ge}", cell_style),
             Paragraph(f"<b>Potencia Continua:</b> {inspeccion.potencia_continua or '-'}", cell_style)],
        ]
        
        tabla_principales = Table(datos_principales, colWidths=[3.5*inch, 3.5*inch])
        tabla_principales.setStyle(TableStyle([
            ('SPAN', (0,0), (1,0)),
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
        
        # ==================== GRUPO ELECTRÓGENO Y ESTANQUE ====================
        titulo_ge = Paragraph("Grupo Electrógeno y Estanque de Combustible", 
                              ParagraphStyle('TituloGEStyle', parent=normal_style,
                                            alignment=TA_CENTER, fontSize=12,
                                            textColor=colors.HexColor("#000000"),
                                            fontName='Helvetica-Bold'))
        
        datos_ge = [
            [titulo_ge, "", "", ""],
            [Paragraph("", cell_style), Paragraph("", cell_style), Paragraph("", cell_style), 
             Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
            [Paragraph("<b>Horas de Funcionamiento</b>", cell_style), 
             Paragraph(str(inspeccion.horas_funcionamiento or '-'), cell_style),
             Paragraph("<b>Limpieza GE Interior</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_ge_interior == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_ge_interior == 'NOK' else "", cell_style)],
            [Paragraph("<b>Cantidad de Arranques</b>", cell_style), 
             Paragraph(str(inspeccion.cantidad_arranques or '-'), cell_style),
             Paragraph("<b>Limpieza Radiador</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_radiador == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_radiador == 'NOK' else "", cell_style)],
            [Paragraph("<b>Nivel de Aceite</b>", cell_style), 
             Paragraph(inspeccion.nivel_aceite or '-', cell_style),
             Paragraph("<b>Visor de Combustible</b>", cell_style),
             Paragraph("X" if inspeccion.visor_combustible == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.visor_combustible == 'NOK' else "", cell_style)],
            [Paragraph("<b>Nivel de Combustible</b>", cell_style), 
             Paragraph(inspeccion.nivel_combustible or '-', cell_style),
             Paragraph("<b>Arranque Automático</b>", cell_style),
             Paragraph("X" if inspeccion.arranque_automatico == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.arranque_automatico == 'NOK' else "", cell_style)],
            [Paragraph("<b>Nivel de Refrigerante</b>", cell_style), 
             Paragraph(inspeccion.nivel_refrigerante or '-', cell_style),
             Paragraph("<b>Limpieza Interior</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_interior == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_interior == 'NOK' else "", cell_style)],
            [Paragraph("<b>Próxima Mantención</b>", cell_style), 
             Paragraph(str(inspeccion.proxima_mantencion or '-'), cell_style),
             Paragraph("<b>Limpieza Exterior</b>", cell_style),
             Paragraph("X" if inspeccion.limpieza_exterior == 'OK' else "", cell_style),
             Paragraph("X" if inspeccion.limpieza_exterior == 'NOK' else "", cell_style)],
            [Paragraph("<b>Estado de Carcasa</b>", cell_style), 
             Paragraph("X" if inspeccion.estado_carcasa == 'OK' else "X" if inspeccion.estado_carcasa == 'NOK' else "", cell_style),
             Paragraph("<b>Cable 5p/4p</b>", cell_style),
             Paragraph(f"{inspeccion.cable_5p_4p or '-'}", cell_style),
             "", ""],
        ]
        
        tabla_ge = Table(datos_ge, colWidths=[2.8*inch, 0.9*inch, 2.3*inch, 0.5*inch, 0.5*inch])
        tabla_ge.setStyle(TableStyle([
            ('SPAN', (0,0), (4,0)),
            ('SPAN', (0,1), (2,1)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('ALIGN', (0,2), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,2), (0,-1), 'LEFT'),
            ('ALIGN', (2,2), (2,-1), 'LEFT'),
        ]))
        elementos.append(tabla_ge)
        
        # Observaciones GE + Fotos
        texto_observaciones = inspeccion.observaciones or 'Sin observaciones'
        datos_obs_fotos = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones}", cell_style)]]
        
        fotos_ge = [('foto_1', 'Foto 1'), ('foto_2', 'Foto 2'), ('foto_3', 'Foto 3')]
        for campo, titulo in fotos_ge:
            foto_nombre = getattr(inspeccion, campo, None)
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = Image(ruta_foto, width=5*inch, height=3*inch)
                        contenido_tabla = Table([
                            [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                            [img]
                        ], colWidths=[5.5*inch])
                        contenido_tabla.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        datos_obs_fotos.append([contenido_tabla])
                    except:
                        pass
        
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
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== ESTADO BREAKER Y BATERÍAS ====================
        titulo_breaker = Paragraph("Estado Breaker y Baterías", 
                                   ParagraphStyle('TituloBreakerStyle', parent=normal_style,
                                                 alignment=TA_CENTER, fontSize=12,
                                                 textColor=colors.HexColor("#000000"),
                                                 fontName='Helvetica-Bold'))
        
        datos_breaker = [
            [titulo_breaker, "", ""],
            [Paragraph("<b>Ítem</b>", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
            [Paragraph("Estado de Pantalla", cell_style),
             "X" if inspeccion.estado_pantalla == 'OK' else "", "X" if inspeccion.estado_pantalla == 'NOK' else ""],
            [Paragraph("Estado de Parada Emergencia", cell_style),
             "X" if inspeccion.estado_parada_emergencia == 'OK' else "", "X" if inspeccion.estado_parada_emergencia == 'NOK' else ""],
            [Paragraph("Estado de Corta Corriente", cell_style),
             "X" if inspeccion.estado_corta_corriente == 'OK' else "", "X" if inspeccion.estado_corta_corriente == 'NOK' else ""],
            [Paragraph("Estado de Selector", cell_style),
             "X" if inspeccion.estado_selector == 'OK' else "", "X" if inspeccion.estado_selector == 'NOK' else ""],
            [Paragraph("Estado de Bornes de Batería", cell_style),
             "X" if inspeccion.estado_bornes_bateria == 'OK' else "", "X" if inspeccion.estado_bornes_bateria == 'NOK' else ""],
            [Paragraph("Estado de Ramal de Cables", cell_style),
             "X" if inspeccion.estado_ramal_cables == 'OK' else "", "X" if inspeccion.estado_ramal_cables == 'NOK' else ""],
            [Paragraph("Estado de Enchufe", cell_style),
             "X" if inspeccion.estado_enchufe == 'OK' else "", "X" if inspeccion.estado_enchufe == 'NOK' else ""],
            [Paragraph("Estado de Cebador", cell_style),
             "X" if inspeccion.estado_cebador == 'OK' else "", "X" if inspeccion.estado_cebador == 'NOK' else ""],
            [Paragraph("Estado de Mangueras", cell_style),
             "X" if inspeccion.estado_mangueras == 'OK' else "", "X" if inspeccion.estado_mangueras == 'NOK' else ""],
            [Paragraph("Estado de Alarmas", cell_style),
             "X" if inspeccion.estado_alarmas == 'OK' else "", "X" if inspeccion.estado_alarmas == 'NOK' else ""],
            [Paragraph("Estado de Extintor", cell_style),
             "X" if inspeccion.estado_extintor == 'OK' else "", "X" if inspeccion.estado_extintor == 'NOK' else ""],
            [Paragraph("Estado de Puertas", cell_style),
             "X" if inspeccion.estado_puertas == 'OK' else "", "X" if inspeccion.estado_puertas == 'NOK' else ""],
            [Paragraph("Estado de Baterías", cell_style),
             "X" if inspeccion.estado_baterias == 'OK' else "", "X" if inspeccion.estado_baterias == 'NOK' else ""],
            [Paragraph("Estado de Ventilador", cell_style),
             "X" if inspeccion.estado_ventilador == 'OK' else "", "X" if inspeccion.estado_ventilador == 'NOK' else ""],
        ]
        
        tabla_breaker = Table(datos_breaker, colWidths=[3.5*inch, 0.8*inch, 0.8*inch])
        tabla_breaker.setStyle(TableStyle([
            ('SPAN', (0,0), (2,0)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#0033a0')),
            ('TEXTCOLOR', (0,1), (-1,1), colors.white),
            ('ALIGN', (1,1), (2,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_breaker)
        
        # Observaciones Breaker + Fotos
        texto_observaciones_breaker = inspeccion.observaciones_breaker or 'Sin observaciones'
        datos_obs_fotos_breaker = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones_breaker}", cell_style)]]
        
        fotos_breaker = [('foto_breaker_1', 'Foto Breaker 1'), ('foto_breaker_2', 'Foto Breaker 2'), ('foto_breaker_3', 'Foto Breaker 3')]
        for campo, titulo in fotos_breaker:
            foto_nombre = getattr(inspeccion, campo, None)
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = Image(ruta_foto, width=5*inch, height=3*inch)
                        contenido_tabla = Table([
                            [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                            [img]
                        ], colWidths=[5.5*inch])
                        contenido_tabla.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        datos_obs_fotos_breaker.append([contenido_tabla])
                    except:
                        pass
        
        tabla_obs_fotos_breaker = Table(datos_obs_fotos_breaker, colWidths=[7.0*inch])
        tabla_obs_fotos_breaker.setStyle(TableStyle([
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
        elementos.append(tabla_obs_fotos_breaker)
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== ESTRUCTURAS, CHASIS Y OTROS ====================
        titulo_estructuras = Paragraph("Estructuras, Chasis y Otros", 
                                       ParagraphStyle('TituloEstGE', parent=normal_style,
                                                     alignment=TA_CENTER, fontSize=12,
                                                     textColor=colors.HexColor("#000000"),
                                                     fontName='Helvetica-Bold'))
        
        datos_estructuras = [
            [titulo_estructuras, "", ""],
            [Paragraph("<b>Ítem</b>", cell_style), Paragraph("<b>OK</b>", cell_style), Paragraph("<b>NOK</b>", cell_style)],
            [Paragraph("Limpieza General", cell_style),
             "X" if inspeccion.limpieza_general == 'OK' else "", "X" if inspeccion.limpieza_general == 'NOK' else ""],
            [Paragraph("Estado de Chasis", cell_style),
             "X" if inspeccion.estado_chasis == 'OK' else "", "X" if inspeccion.estado_chasis == 'NOK' else ""],
            [Paragraph(f"Cantidad de Cuñas: {inspeccion.cantidad_cunas or '-'}", cell_style), "", ""],
            [Paragraph("Checkpoints", cell_style),
             "X" if inspeccion.checkpoints == 'OK' else "", "X" if inspeccion.checkpoints == 'NOK' else ""],
            [Paragraph("Presión de Neumáticos", cell_style),
             "X" if inspeccion.presion_neumaticos == 'OK' else "", "X" if inspeccion.presion_neumaticos == 'NOK' else ""],
            [Paragraph("Estado de Jaula", cell_style),
             "X" if inspeccion.estado_jaula == 'OK' else "", "X" if inspeccion.estado_jaula == 'NOK' else ""],
            [Paragraph("Estado de Candados", cell_style),
             "X" if inspeccion.estado_candados == 'OK' else "", "X" if inspeccion.estado_candados == 'NOK' else ""],
            [Paragraph("Nivelación de Carro", cell_style),
             "X" if inspeccion.nivelacion_carro == 'OK' else "", "X" if inspeccion.nivelacion_carro == 'NOK' else ""],
            [Paragraph("Patas de Posicionamiento", cell_style),
             "X" if inspeccion.patas_posicionamiento == 'OK' else "", "X" if inspeccion.patas_posicionamiento == 'NOK' else ""],
            [Paragraph("Manivelas Izajes de Pata", cell_style),
             "X" if inspeccion.manivelas_izajes == 'OK' else "", "X" if inspeccion.manivelas_izajes == 'NOK' else ""],
        ]
        
        tabla_estructuras = Table(datos_estructuras, colWidths=[3.5*inch, 0.8*inch, 0.8*inch])
        tabla_estructuras.setStyle(TableStyle([
            ('SPAN', (0,0), (2,0)),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#0033a0')),
            ('TEXTCOLOR', (0,1), (-1,1), colors.white),
            ('ALIGN', (1,1), (2,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elementos.append(tabla_estructuras)
        
        # Observaciones Estructuras + Fotos
        texto_observaciones_estructuras = inspeccion.observaciones_estructuras or 'Sin observaciones'
        datos_obs_fotos_estructuras = [[Paragraph(f"<b>Observaciones:</b> {texto_observaciones_estructuras}", cell_style)]]
        
        fotos_estructuras = [('foto_estructura_1', 'Foto Estructura 1'), 
                             ('foto_estructura_2', 'Foto Estructura 2'), 
                             ('foto_estructura_3', 'Foto Estructura 3')]
        for campo, titulo in fotos_estructuras:
            foto_nombre = getattr(inspeccion, campo, None)
            if foto_nombre:
                ruta_foto = os.path.join('static/uploads', foto_nombre)
                if os.path.exists(ruta_foto):
                    try:
                        img = Image(ruta_foto, width=5*inch, height=3*inch)
                        contenido_tabla = Table([
                            [Paragraph(f"<b>{titulo}:</b>", cell_style)],
                            [img]
                        ], colWidths=[5.5*inch])
                        contenido_tabla.setStyle(TableStyle([
                            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                            ('TOPPADDING', (0,0), (-1,-1), 2),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                        ]))
                        datos_obs_fotos_estructuras.append([contenido_tabla])
                    except:
                        pass
        
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
        elementos.append(Spacer(1, 0.2*inch))
        
        # ==================== LEVANTAMIENTO DE FOTOGRAFÍAS (8 PUNTOS) ====================
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
        
        def crear_tabla_foto_ge(titulo, foto_nombre):
            if not foto_nombre:
                return None
            ruta_foto = os.path.join('static/uploads', foto_nombre)
            if not os.path.exists(ruta_foto):
                return None
            try:
                img = Image(ruta_foto, width=5*inch, height=3*inch)
                contenido_celda = [Paragraph(f"<b>{titulo}</b>", cell_style), img]
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
        
        puntos_fotos_ge = [
            ("1. Fotografía del estado del sitio previo al comienzo de trabajos", 'foto_lev_1'),
            ("2. Fotografía del panel de control del generador auxiliar", 'foto_lev_2'),
            ("3. Fotografía de neumáticos", 'foto_lev_3'),
            ("4. Fotografía del GE Auxiliar al término de la mantención", 'foto_lev_4'),
            ("5. Fotografía adicional 1", 'foto_lev_5'),
            ("6. Fotografía adicional 2", 'foto_lev_6'),
            ("7. Fotografía adicional 3", 'foto_lev_7'),
            ("8. Fotografía adicional 4", 'foto_lev_8'),
        ]
        
        for titulo, campo_foto in puntos_fotos_ge:
            foto_nombre = getattr(inspeccion, campo_foto, None)
            tabla = crear_tabla_foto_ge(titulo, foto_nombre)
            if tabla:
                elementos.append(tabla)
    
    # Construir PDF
    doc.build(elementos)
    buffer.seek(0)
    
    # Nombre del archivo
    if tipo == 'cow':
        nombre_sitio_pdf = inspeccion.sitio_ref.nombre_sitio if inspeccion.sitio_ref else 'sin_sitio'
    else:
        nombre_sitio_pdf = inspeccion.nombre_ge or 'sin_sitio'
    
    nombre_base = nombre_sitio_pdf.replace(" ", "_").replace("/", "_")[:50]
    filename = f"{nombre_base}_{inspeccion.fecha.replace('/', '-')}.pdf"
    
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

# 6. SEXTO crear tablas
with app.app_context():
    db.create_all()

# 7. SÉPTIMO ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)