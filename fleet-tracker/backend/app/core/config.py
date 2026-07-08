import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fleet.db")
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-esta-clave-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8

# --- Proveedor GPS activo ---
# "mock" mientras no haya acceso a la GAP. Cambiar a "gap" cuando esté
# la documentación de API/credenciales, y completar GAPProvider.
GPS_PROVIDER = os.getenv("GPS_PROVIDER", "mock")
GAP_BASE_URL = os.getenv("GAP_BASE_URL", "")
GAP_API_KEY = os.getenv("GAP_API_KEY", "")
