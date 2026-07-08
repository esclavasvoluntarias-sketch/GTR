"""
Adaptador de proveedor GPS.

Esta es la pieza clave para no quedar atados a la GAP: toda la app habla
contra la interfaz `GPSProvider`. Hoy usamos `MockGPSProvider` (datos
simulados). El día que tengan credenciales/API de la GAP, se escribe
`GAPProvider(GPSProvider)` implementando los mismos métodos y se cambia
UNA línea en `core/config.py`. Ningún otro módulo del sistema cambia.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import random


@dataclass
class LecturaCruda:
    gps_device_id: str
    latitud: float
    longitud: float
    velocidad: float
    encendido: bool
    timestamp: datetime


class GPSProvider(ABC):
    """Contrato que cualquier proveedor GPS (mock o GAP real) debe cumplir."""

    @abstractmethod
    def obtener_lecturas(self) -> list[LecturaCruda]:
        """Devuelve la última lectura conocida de cada dispositivo activo."""
        raise NotImplementedError

    @abstractmethod
    def obtener_lectura_por_dispositivo(self, gps_device_id: str) -> LecturaCruda | None:
        raise NotImplementedError


class MockGPSProvider(GPSProvider):
    """
    Simulador para desarrollo y demo. Genera posiciones y estados
    plausibles alrededor de un punto base, con algunos móviles
    intencionalmente "apagados" o "sin loguear" para poder probar
    el motor de alertas end-to-end.
    """

    def __init__(self, device_ids: list[str], base_lat: float = -31.4201, base_lon: float = -64.1888):
        self._device_ids = device_ids
        self._base_lat = base_lat
        self._base_lon = base_lon

    def obtener_lecturas(self) -> list[LecturaCruda]:
        return [self._simular(dev_id) for dev_id in self._device_ids]

    def obtener_lectura_por_dispositivo(self, gps_device_id: str) -> LecturaCruda | None:
        if gps_device_id not in self._device_ids:
            return None
        return self._simular(gps_device_id)

    def _simular(self, dev_id: str) -> LecturaCruda:
        random.seed(dev_id + datetime.utcnow().strftime("%Y%m%d%H%M"))
        encendido = random.random() > 0.15
        return LecturaCruda(
            gps_device_id=dev_id,
            latitud=self._base_lat + random.uniform(-0.05, 0.05),
            longitud=self._base_lon + random.uniform(-0.05, 0.05),
            velocidad=random.uniform(0, 60) if encendido else 0.0,
            encendido=encendido,
            timestamp=datetime.utcnow(),
        )


class GAPProvider(GPSProvider):
    """
    Implementación real contra la GAP. PENDIENTE: completar cuando
    haya documentación de API / credenciales.

    Se espera algo del estilo:
        def __init__(self, base_url: str, api_key: str): ...
        def obtener_lecturas(self) -> list[LecturaCruda]:
            resp = httpx.get(f"{base_url}/vehicles/positions", headers=...)
            return [self._parse(v) for v in resp.json()]
    """

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key

    def obtener_lecturas(self) -> list[LecturaCruda]:
        raise NotImplementedError(
            "GAPProvider aún no implementado: falta documentación de API de la GAP."
        )

    def obtener_lectura_por_dispositivo(self, gps_device_id: str) -> LecturaCruda | None:
        raise NotImplementedError(
            "GAPProvider aún no implementado: falta documentación de API de la GAP."
        )
