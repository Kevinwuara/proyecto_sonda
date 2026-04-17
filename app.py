from flask import Flask, render_template, redirect, url_for, request, session
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from forms_cow import InspeccionCOWForm
from werkzeug.utils import secure_filename
import os

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