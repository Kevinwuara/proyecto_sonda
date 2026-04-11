from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    # Crear tablas
    db.create_all()
    
    # Verificar si ya existen usuarios
    if Usuario.query.count() == 0:
        # Crear usuario Técnico
        tecnico = Usuario(
            username='tecnico',
            password=generate_password_hash('tec123'),
            nombre='Carlos Técnico',
            rol='tecnico',
            email='tecnico@sonda.cl'
        )
        
        # Crear usuario Supervisor
        supervisor = Usuario(
            username='supervisor',
            password=generate_password_hash('sup123'),
            nombre='Ana Supervisora',
            rol='supervisor',
            email='supervisor@sonda.cl'
        )
        
        db.session.add(tecnico)
        db.session.add(supervisor)
        db.session.commit()
        
        print("Usuarios creados correctamente")
    else:
        print("Los usuarios ya existen")