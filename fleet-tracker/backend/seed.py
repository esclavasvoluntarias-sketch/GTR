"""Carga datos de ejemplo para poder probar el sistema de punta a punta."""
from datetime import datetime
from app.core.database import init_db, SessionLocal
from app.models.models import BaseDespacho, Agente, Movil, ServicioProyectado, TipoServicio

init_db()
db = SessionLocal()

bases_codigos = ["6001", "MECA", "10541", "13305"]
bases = {}
for codigo in bases_codigos:
    b = db.query(BaseDespacho).filter_by(codigo=codigo).first()
    if not b:
        b = BaseDespacho(codigo=codigo, nombre=f"Base {codigo}")
        db.add(b)
        db.flush()
    bases[codigo] = b

for i in range(1, 21):
    ident = f"MOV-{i:03d}"
    if db.query(Movil).filter_by(identificador=ident).first():
        continue
    agente = Agente(legajo=f"L{i:04d}", nombre=f"Agente {i}")
    db.add(agente)
    db.flush()

    base_codigo = bases_codigos[i % len(bases_codigos)]
    movil = Movil(
        identificador=ident,
        gps_device_id=f"GPS-{i:03d}",
        tipo_servicio=TipoServicio.TRASLADOS_6001 if i % 2 == 0 else TipoServicio.MECANICA,
        base_id=bases[base_codigo].id,
        agente_id=agente.id,
    )
    db.add(movil)
    db.flush()

    hoy = datetime.utcnow().date()
    servicio = ServicioProyectado(
        movil_id=movil.id,
        fecha=datetime(hoy.year, hoy.month, hoy.day),
        hora_inicio_turno="06:00",
        hora_fin_turno="14:00",
        tipo_servicio=movil.tipo_servicio,
        coeficiente_operativo=1.0,
    )
    db.add(servicio)

db.commit()
print("Datos de ejemplo cargados: 4 bases, 20 móviles, 20 servicios proyectados para hoy.")
