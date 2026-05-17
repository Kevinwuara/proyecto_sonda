from app import app, db, Sitio

def poblar_sitios():
    sitios = [
        # nombre_sitio, area, tipo, ubicacion
        ("COW 01 HD (Esperanza Sur) Área Autónoma", "Área Autónoma", "HD", "Esperanza Sur"),
        ("COW 02 HD (Esperanza Sur) Área Convencional", "Área Convencional", "HD", "Esperanza Sur"),
        ("COW 03 HD (Esperanza Sur) Área Convencional", "Área Convencional", "HD", "Esperanza Sur"),
        ("COW 04 HD (Esperanza Sur) Área Convencional", "Área Convencional", "HD", "Esperanza Sur"),
        ("COW 05 FAST SITE (Esperanza sur) Fuera Área Mina", "Fuera Área Mina", "FAST SITE", "Esperanza Sur"),
        ("COW 06 HD (Esperanza Sur) Área Autónoma", "Área Autónoma", "HD", "Esperanza Sur"),
        ("COW 09 HD (OXE Encuentro) Fuera Área Mina", "Fuera Área Mina", "HD", "OXE Encuentro"),
        ("COW 10 HD (OXE Encuentro) Fuera Área Mina", "Fuera Área Mina", "HD", "OXE Encuentro"),
        ("COW 11 Light (OXE Encuentro) Área Mina", "Área Mina", "LIGHT", "OXE Encuentro"),
        ("COW 13 HD (OXE Encuentro) Área Mina", "Área Mina", "HD", "OXE Encuentro"),
        ("COW 14 HD (OXE Encuentro) Área Mina", "Área Mina", "HD", "OXE Encuentro"),
        ("COW 19 LIGHT (Esperanza sur) Área Convencional", "Área Convencional", "LIGHT", "Esperanza Sur"),
        ("COW 20 LIGHT (Esperanza Sur) Área Convencional", "Área Convencional", "LIGHT", "Esperanza Sur"),
        ("COW 21 LIGHT (Esperanza Sur) Área Autónoma", "Área Autónoma", "LIGHT", "Esperanza Sur"),
        ("COW 22 LIGHT (Esperanza sur) Área Autónoma", "Área Autónoma", "LIGHT", "Esperanza Sur"),
        ("COW 23 LIGHT (Esperanza sur) Área Autónoma", "Área Autónoma", "LIGHT", "Esperanza Sur"),
    ]
    
    with app.app_context():
        # Limpiar sitios existentes (opcional)
        Sitio.query.delete()
        
        for nombre, area, tipo, ubicacion in sitios:
            sitio = Sitio(
                nombre_sitio=nombre,
                area=area,
                tipo=tipo,
                ubicacion=ubicacion,
                activo=True
            )
            db.session.add(sitio)
        
        db.session.commit()
        print(f"✅ {len(sitios)} sitios agregados correctamente")

if __name__ == "__main__":
    poblar_sitios()