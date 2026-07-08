"""
Motor de alertas: compara planificación (ServicioProyectado) vs. estado
real reportado por el GPSProvider, y genera Alertas con severidad.

Reglas base (ajustables):
- Móvil planificado, sin login del sistema pasados N minutos del inicio
  de turno -> ADVERTENCIA. Pasados 2N minutos -> CRITICA.
- Móvil planificado, sin señal GPS / apagado durante el turno -> CRITICA.
- Móvil logueado pero fuera del radio esperado de su base -> ADVERTENCIA.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.models import (
    Movil, ServicioProyectado, LecturaGPS, Alerta, SeveridadAlerta
)

MINUTOS_TOLERANCIA_ADVERTENCIA = 10
MINUTOS_TOLERANCIA_CRITICA = 25


def evaluar_flota(db: Session, ahora: datetime | None = None) -> list[Alerta]:
    ahora = ahora or datetime.utcnow()
    hoy = ahora.date()

    servicios_hoy = (
        db.query(ServicioProyectado)
        .filter(ServicioProyectado.fecha >= hoy)
        .filter(ServicioProyectado.fecha < hoy + timedelta(days=1))
        .all()
    )

    nuevas_alertas: list[Alerta] = []

    for servicio in servicios_hoy:
        movil = db.query(Movil).get(servicio.movil_id)
        if not movil or not movil.activo:
            continue

        hora_inicio = datetime.strptime(servicio.hora_inicio_turno, "%H:%M").time()
        inicio_turno_dt = datetime.combine(hoy, hora_inicio)

        if ahora < inicio_turno_dt:
            continue  # el turno todavía no arrancó

        minutos_transcurridos = (ahora - inicio_turno_dt).total_seconds() / 60

        ultima_lectura = (
            db.query(LecturaGPS)
            .filter(LecturaGPS.movil_id == movil.id)
            .order_by(LecturaGPS.timestamp.desc())
            .first()
        )

        logueado = ultima_lectura.logueado_sistema if ultima_lectura else False

        if logueado:
            continue  # cumple planificación, no genera alerta

        severidad = None
        if minutos_transcurridos >= MINUTOS_TOLERANCIA_CRITICA:
            severidad = SeveridadAlerta.CRITICA
        elif minutos_transcurridos >= MINUTOS_TOLERANCIA_ADVERTENCIA:
            severidad = SeveridadAlerta.ADVERTENCIA

        if severidad:
            alerta = Alerta(
                movil_id=movil.id,
                severidad=severidad,
                motivo=f"Sin login del sistema. Turno inició hace {int(minutos_transcurridos)} min.",
                minutos_desvio=minutos_transcurridos,
                timestamp=ahora,
            )
            db.add(alerta)
            nuevas_alertas.append(alerta)

    db.commit()
    return nuevas_alertas
