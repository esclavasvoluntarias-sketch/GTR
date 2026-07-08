from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import (
    BaseDespacho, Movil, ServicioProyectado, LecturaGPS, Alerta, SeveridadAlerta
)
from app.models.schemas import KPIResumen

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("/resumen", response_model=list[KPIResumen])
def resumen_por_base(db: Session = Depends(get_db)):
    """Cumplimiento hoy: proyectados vs. logueados, por base."""
    hoy = datetime.utcnow().date()
    resultado = []

    for base in db.query(BaseDespacho).all():
        moviles_base = db.query(Movil).filter(Movil.base_id == base.id, Movil.activo.is_(True)).all()
        movil_ids = [m.id for m in moviles_base]

        proyectados = (
            db.query(ServicioProyectado)
            .filter(ServicioProyectado.movil_id.in_(movil_ids))
            .filter(ServicioProyectado.fecha >= hoy)
            .filter(ServicioProyectado.fecha < hoy + timedelta(days=1))
            .count()
        )

        logueados = 0
        for mid in movil_ids:
            ultima = (
                db.query(LecturaGPS)
                .filter(LecturaGPS.movil_id == mid)
                .order_by(LecturaGPS.timestamp.desc())
                .first()
            )
            if ultima and ultima.logueado_sistema:
                logueados += 1

        criticas = (
            db.query(Alerta)
            .filter(Alerta.movil_id.in_(movil_ids))
            .filter(Alerta.severidad == SeveridadAlerta.CRITICA)
            .filter(Alerta.resuelta.is_(False))
            .count()
        )
        advertencias = (
            db.query(Alerta)
            .filter(Alerta.movil_id.in_(movil_ids))
            .filter(Alerta.severidad == SeveridadAlerta.ADVERTENCIA)
            .filter(Alerta.resuelta.is_(False))
            .count()
        )

        cumplimiento = round((logueados / proyectados) * 100, 1) if proyectados else 0.0

        resultado.append(
            KPIResumen(
                base=base.codigo,
                proyectados=proyectados,
                logueados=logueados,
                cumplimiento_pct=cumplimiento,
                alertas_criticas=criticas,
                alertas_advertencia=advertencias,
            )
        )
    return resultado


@router.get("/impacto-faltante")
def impacto_faltante(movil_id: int, horas: int = 4, db: Session = Depends(get_db)):
    """
    Análisis de impacto hora a hora si un móvil específico falta:
    cuántos servicios proyectados de su base quedan por debajo del
    coeficiente operativo esperado en las próximas N horas.
    """
    movil = db.query(Movil).get(movil_id)
    if not movil:
        return {"error": "móvil no encontrado"}

    hoy = datetime.utcnow().date()
    servicios_base = (
        db.query(ServicioProyectado)
        .join(Movil, Movil.id == ServicioProyectado.movil_id)
        .filter(Movil.base_id == movil.base_id)
        .filter(ServicioProyectado.fecha >= hoy)
        .filter(ServicioProyectado.fecha < hoy + timedelta(days=1))
        .all()
    )

    total_coef = sum(s.coeficiente_operativo for s in servicios_base)
    coef_movil = sum(
        s.coeficiente_operativo for s in servicios_base if s.movil_id == movil_id
    )
    impacto_pct = round((coef_movil / total_coef) * 100, 1) if total_coef else 0.0

    return {
        "movil": movil.identificador,
        "base": movil.base.codigo if movil.base else "-",
        "coeficiente_aportado": coef_movil,
        "coeficiente_total_base": total_coef,
        "impacto_estimado_pct": impacto_pct,
        "horizonte_horas": horas,
    }
