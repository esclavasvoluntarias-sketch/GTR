# Seguimiento de Flota en Tiempo Real

Aplicación para monitorear el estado GPS de la flota, comparar servicios
proyectados vs. reales, generar alertas por severidad y llevar KPIs de
cumplimiento por base (6001, MECA, 10541, 13305).

## Arquitectura

```
fleet-tracker/
├── backend/          FastAPI + SQLAlchemy (Python)
│   └── app/
│       ├── api/       endpoints (auth, flota, alertas, kpis, carga)
│       ├── models/    modelos de datos y schemas
│       ├── services/  motor de alertas + adaptador GPS
│       └── core/      config, DB, seguridad
├── frontend/          React + Vite, responsive (PWA instalable en celu)
└── docker-compose.yml despliegue on-premise con un comando
```

### La pieza clave: adaptador GPS intercambiable

Todo el sistema habla contra la interfaz `GPSProvider`
(`backend/app/services/gps_provider.py`). Hoy corre con
`MockGPSProvider` (datos simulados) porque todavía no hay acceso a la
API de la GAP. El día que tengan documentación/credenciales:

1. Completar `GAPProvider` en el mismo archivo (ya tiene el esqueleto).
2. Cambiar `GPS_PROVIDER=gap` y cargar `GAP_BASE_URL`/`GAP_API_KEY` en
   las variables de entorno.

Ningún otro módulo del sistema necesita cambios.

## Correr en desarrollo (sin Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python seed.py          # carga datos de ejemplo (4 bases, 20 móviles)
uvicorn app.main:app --reload
```
Backend disponible en `http://localhost:8000`. Docs interactivas en
`http://localhost:8000/docs`.

Usuario demo: `admin` / `admin123` (cambiar `ADMIN_PASSWORD` en
producción).

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Frontend disponible en `http://localhost:5173` (proxea `/api` al
backend automáticamente).

## Correr en producción (on-premise, con Docker)

```bash
docker compose up -d --build
```

Esto levanta:
- PostgreSQL (persistente, con volumen)
- Backend FastAPI en el puerto 8000
- Frontend (nginx) en el puerto 80

**Antes de ir a producción real:**
- Cambiar `SECRET_KEY`, `ADMIN_PASSWORD` y la contraseña de Postgres en
  `docker-compose.yml`.
- Restringir `allow_origins` en `backend/app/main.py` (hoy está en `*`
  para desarrollo).
- Definir un sistema de usuarios real (hoy hay un único usuario demo
  hardcodeado en `backend/app/api/auth.py`).

## Uso en celular

El frontend es una PWA: desde el navegador del celu, "Agregar a
pantalla de inicio" la instala como app, sin pasar por Google Play /
App Store. Funciona igual en compu.

## Carga masiva por Excel

Dos plantillas aceptadas (ver detalle de columnas en la pestaña "Carga
masiva" de la app):
- **Nómina**: identificador, gps_device_id, base, tipo_servicio, agente_legajo, agente_nombre
- **Planificación semanal**: identificador, fecha, hora_inicio, hora_fin, tipo_servicio, coeficiente

## Estado actual / pendientes

- [x] Backend funcional: auth, sincronización GPS (mock), motor de
      alertas, KPIs por base, carga masiva por Excel.
- [x] Frontend funcional: dashboard, flota en vivo, alertas con
      justificación (FCO/VAC/QRX/ENF/DOC), carga masiva.
- [x] Dockerizado para despliegue on-premise.
- [ ] **Integración real con la GAP** — bloqueado hasta conseguir
      documentación de API / credenciales.
- [ ] Sistema de usuarios múltiples con roles.
- [ ] Notificaciones push para alertas críticas.
- [ ] Historial de indicadores por período (hoy el motor de alertas
      trabaja sobre el día actual; falta la vista de series históricas).
