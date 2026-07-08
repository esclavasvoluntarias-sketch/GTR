from pydantic import BaseModel
from datetime import datetime
from app.models.models import SeveridadAlerta, TipoServicio


class MovilEstado(BaseModel):
    id: int
    identificador: str
    base: str
    tipo_servicio: str
    agente: str | None
    encendido: bool
    logueado_sistema: bool
    velocidad: float | None
    ultima_actualizacion: datetime | None

    class Config:
        from_attributes = True


class AlertaOut(BaseModel):
    id: int
    movil_id: int
    identificador_movil: str
    severidad: SeveridadAlerta
    motivo: str
    minutos_desvio: float
    timestamp: datetime
    resuelta: bool
    justificacion: str | None

    class Config:
        from_attributes = True


class JustificarAlerta(BaseModel):
    justificacion: str  # FCO, VAC, QRX, ENF, DOC u otra nota


class KPIResumen(BaseModel):
    base: str
    proyectados: int
    logueados: int
    cumplimiento_pct: float
    alertas_criticas: int
    alertas_advertencia: int


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
