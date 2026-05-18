Sistema Web de Inspección SONDA

Descripción
Sistema web para gestión digital de inspecciones de equipos de telecomunicaciones (COW, GE Auxiliar, Desplazamiento, Monitoreo Noche).

Tecnologías
- Backend: Flask (Python)
- Frontend: HTML5, CSS3, Jinja2
- Base de datos: SQLite
- Seguridad: Werkzeug (cifrado), sesiones Flask

Acceso al sistema (Hosting)
🌐 URL: https://proyecto-sonda.onrender.com/login

Credenciales de acceso
| Perfil | Usuario | Contraseña |
|--------|---------|-------------|
| Técnico | `tecnico` | `tec123` |
| Supervisor | `supervisor` | `sup123` |

Estructura de Base de Datos
- Modelo relacional en 3FN
- 9+ tablas: usuario, sitio, inspeccion_cow, inspeccion_ge, desplazamiento_cow, monitoreo_noche, fotografia, mejora, estados_inspeccion
- Scripts en `/database/`

Autor
Kevin Angelo Alberto Alarcón Iturra
