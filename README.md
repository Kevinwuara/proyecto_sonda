# Sistema Web de Inspección SONDA

Sistema web para gestión digital de inspecciones de equipos de telecomunicaciones (COW, GE Auxiliar, Desplazamiento).

## Tecnologías
- Python + Flask
- SQLite + SQLAlchemy
- HTML + CSS (responsive)

## Acceso

**URL:** `http://127.0.0.1:5000` (ejecutar localmente)

### Credenciales
| Perfil | Usuario | Contraseña |
|--------|---------|-------------|
| Técnico | tecnico | tec123 |
| Supervisor | supervisor | sup123 |

## Instalación
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
