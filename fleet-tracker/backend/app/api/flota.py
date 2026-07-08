from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.config import GPS_PROVIDER, GAP_BASE_URL, GAP_API_KEY
from app.models.models import Movil, LecturaGPS, BaseDespacho, Agente
from app.models.schemas import MovilEstado
from app.services.gps_provider import MockGPSProvider, GAPProvider

router = APIRouter(prefix="/api/flota", tags=["flota"])


def get_provider(db: Session):
    device_ids = [m.gps_device_id for m in db.query(Movil).filter(Movil.gps_device_id.isnot(None)).all()]
    if GPS_PROVIDER == "gap":
        return GAPProvider(base_url=GAP_BASE_URL, api_key=GAP_API_KEY)
    return MockGPSProvider(device_ids=device_ids)


@router.post("/sincronizar")
def sincronizar_lecturas(db: Session = Depends(get_db)):
    """Pide al proveedor GPS activo el estado actual y lo persiste."""
    provider = get_provider(db)
    lecturas = provider.obtener_lecturas()
    creadas = 0
    for lectura in lecturas:
        movil = db.query(Movil).filter(Movil.gps_device_id == lectura.gps_device_id).first()
        if not movil:
            continue
        registro = LecturaGPS(
            movil_id=movil.id,
            timestamp=lectura.timestamp,
            latitud=lectura.latitud,
            longitud=lectura.longitud,
            velocidad=lectura.velocidad,
            encendido=lectura.encendido,
            # el "login del sistema" es un dato aparte del GPS crudo;
            # en el mock lo simulamos ligado a "encendido" para poder probar.
            logueado_sistema=lectura.encendido,
        )
        db.add(registro)
        creadas += 1
    db.commit()
    return {"lecturas_procesadas": creadas, "proveedor": GPS_PROVIDER}


@router.get("/estado", response_model=list[MovilEstado])
def estado_flota(base: str | None = None, db: Session = Depends(get_db)):
    """Estado actual (última lectura) de todos los móviles, opcionalmente filtrado por base."""
    query = db.query(Movil).filter(Movil.activo.is_(True))
    if base:
        query = query.join(BaseDespacho).filter(BaseDespacho.codigo == base)

    resultado = []
    for movil in query.all():
        ultima = (
            db.query(LecturaGPS)
            .filter(LecturaGPS.movil_id == movil.id)
            .order_by(LecturaGPS.timestamp.desc())
            .first()
        )
        resultado.append(
            MovilEstado(
                id=movil.id,
                identificador=movil.identificador,
                base=movil.base.codigo if movil.base else "-",
                tipo_servicio=movil.tipo_servicio.value,
                agente=movil.agente.nombre if movil.agente else None,
                encendido=ultima.encendido if ultima else False,
                logueado_sistema=ultima.logueado_sistema if ultima else False,
                velocidad=ultima.velocidad if ultima else None,
                ultima_actualizacion=ultima.timestamp if ultima else None,
            )
        )
    return resultado
