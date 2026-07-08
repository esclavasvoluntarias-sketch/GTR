"""
Modelos de datos del sistema de seguimiento de flota.

Entidades principales:
- Movil: unidad de la flota
- Agente: chofer/operador vinculado a un móvil
- Base: hub de despacho (6001, MECA, 10541, 13305, etc.)
- ServicioProyectado: planificación semanal de turnos
- LecturaGPS: posición/estado reportado por la GAP (o el mock)
- Alerta: evento generado por el motor de reglas
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum
)
from sqlalchemy.orm import relationship, declarative_base
import enum
import datetime

Base = declarative_base()


class SeveridadAlerta(str, enum.Enum):
    INFO = "info"
    ADVERTENCIA = "advertencia"
    CRITICA = "critica"


class TipoServicio(str, enum.Enum):
    TRASLADOS_6001 = "traslados_6001"
    MECANICA = "mecanica"
    OTRO = "otro"


class BaseDespacho(Base):
    __tablename__ = "bases"
    id = Column(Integer, primary_key=True)
    codigo = Column(String, unique=True, nullable=False)  # 6001, MECA, 10541, 13305
    nombre = Column(String, nullable=False)

    moviles = relationship("Movil", back_populates="base")


class Agente(Base):
    __tablename__ = "agentes"
    id = Column(Integer, primary_key=True)
    legajo = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

    moviles = relationship("Movil", back_populates="agente")


class Movil(Base):
    __tablename__ = "moviles"
    id = Column(Integer, primary_key=True)
    identificador = Column(String, unique=True, nullable=False)  # patente / código interno
    gps_device_id = Column(String, unique=True, nullable=True)   # ID del dispositivo en la GAP
    tipo_servicio = Column(Enum(TipoServicio), nullable=False)
    base_id = Column(Integer, ForeignKey("bases.id"))
    agente_id = Column(Integer, ForeignKey("agentes.id"), nullable=True)
    activo = Column(Boolean, default=True)

    base = relationship("BaseDespacho", back_populates="moviles")
    agente = relationship("Agente", back_populates="moviles")


class ServicioProyectado(Base):
    """Planificación semanal: qué móvil debería estar operando, cuándo y dónde."""
    __tablename__ = "servicios_proyectados"
    id = Column(Integer, primary_key=True)
    movil_id = Column(Integer, ForeignKey("moviles.id"))
    fecha = Column(DateTime, nullable=False)
    hora_inicio_turno = Column(String, nullable=False)  # "06:00"
    hora_fin_turno = Column(String, nullable=False)
    tipo_servicio = Column(Enum(TipoServicio), nullable=False)
    coeficiente_operativo = Column(Float, default=1.0)


class LecturaGPS(Base):
    """Última lectura reportada por el proveedor GPS (real o mock)."""
    __tablename__ = "lecturas_gps"
    id = Column(Integer, primary_key=True)
    movil_id = Column(Integer, ForeignKey("moviles.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    velocidad = Column(Float, nullable=True)
    encendido = Column(Boolean, default=False)
    logueado_sistema = Column(Boolean, default=False)  # primer login del día ya ocurrió


class Alerta(Base):
    __tablename__ = "alertas"
    id = Column(Integer, primary_key=True)
    movil_id = Column(Integer, ForeignKey("moviles.id"))
    severidad = Column(Enum(SeveridadAlerta), nullable=False)
    motivo = Column(String, nullable=False)
    minutos_desvio = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    resuelta = Column(Boolean, default=False)
    justificacion = Column(String, nullable=True)  # FCO/VAC/QRX/ENF/DOC u otra nota
