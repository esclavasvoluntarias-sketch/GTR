from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Alerta, Movil
from app.models.schemas import AlertaOut, JustificarAlerta
from app.services.alertas_engine import evaluar_flota

router = APIRouter(prefix="/api/alertas", tags=["alertas"])


@router.post("/evaluar")
def evaluar(db: Session = Depends(get_db)):
    """Corre el motor de reglas: planificado vs. real, genera alertas nuevas."""
    nuevas = evaluar_flota(db)
    return {"alertas_generadas": len(nuevas)}


@router.get("", response_model=list[AlertaOut])
def listar_alertas(resueltas: bool = False, db: Session = Depends(get_db)):
    query = db.query(Alerta).filter(Alerta.resuelta.is_(resueltas)).order_by(Alerta.timestamp.desc())
    salida = []
    for a in query.all():
        movil = db.query(Movil).get(a.movil_id)
        salida.append(
            AlertaOut(
                id=a.id,
                movil_id=a.movil_id,
                identificador_movil=movil.identificador if movil else "?",
                severidad=a.severidad,
                motivo=a.motivo,
                minutos_desvio=a.minutos_desvio,
                timestamp=a.timestamp,
                resuelta=a.resuelta,
                justificacion=a.justificacion,
            )
        )
    return salida


@router.patch("/{alerta_id}/justificar")
def justificar_alerta(alerta_id: int, body: JustificarAlerta, db: Session = Depends(get_db)):
    alerta = db.query(Alerta).get(alerta_id)
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta.justificacion = body.justificacion
    alerta.resuelta = True
    db.commit()
    return {"ok": True}
