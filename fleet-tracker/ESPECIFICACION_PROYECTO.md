# Especificación de proyecto: Seguimiento de Flota en Tiempo Real — SOS · Red de Asistencia

> Este documento está pensado para pegarse directamente en el asistente de GitHub (Copilot Workspace / Copilot Chat) como brief de proyecto o como cuerpo de un issue inicial. Contiene el contexto de negocio, la estructura real de datos (extraída de los Excel de la operación), la arquitectura ya validada, y el alcance funcional completo.

---

## 1. Contexto y objetivo

**Quién opera esto:** un gestor en tiempo real (Ridicula) responsable de monitorear el despacho de vehículos de una red de auxilio vial (SOS · Red de Asistencia) en Argentina, sobre 4 bases y una flota de 300+ móviles.

**Problema actual:** existe un sistema de reporting mensual en Excel (`Seguimiento_Trafico_Local_Abril_2026_FINAL_4.xlsx`) que es sólido para análisis histórico y cierre de mes, pero no da visibilidad en tiempo real de qué móvil no se logueó hoy y hace cuánto. El objetivo es una aplicación que dé esa visibilidad en vivo, conectándose eventualmente al sistema GPS de la empresa (referido como "la GAP"), y que además incorpore proyecciones por tipo de servicio, análisis de impacto ante faltantes, planificación semanal y dashboards de cumplimiento — sin perder la lógica y terminología ya validada en el Excel.

**Objetivo del producto:** centralizar la operación de despacho, mejorar la toma de decisiones en tiempo real y optimizar la disponibilidad de la flota.

---

## 2. Glosario de dominio (usar estos términos exactos en código, UI y commits)

| Término | Significado |
|---|---|
| Móvil | Unidad de la flota (vehículo) |
| Base | Hub de despacho: `6001`, `MECA`, `10541`, `13305` |
| Turno | Horario planificado de un móvil, formato `HH:MM-HH:MM` |
| Logueo / login | Marca de inicio de actividad de un móvil en el sistema de despacho |
| Primer loguin del día | Único dato de login que exporta el sistema real de despacho (no hay logout/egreso en el feed en vivo) |
| Ingreso / Egreso | Datos completos de entrada y salida, disponibles en el reporting mensual histórico (`IMPORTAR_REAL`), pero **no** en el feed en tiempo real |
| GAP | Sistema GPS de la empresa. Sin documentación de API todavía — acceso pendiente |
| FCO / VAC / QRX / ENF / DOC | Códigos de ausencia/franco que reemplazan el horario de turno en la nómina |
| CUMPLIÓ / TARDÍO / ANTICIPADO / AUSENCIA | Estados de puntualidad de un móvil frente a su turno planificado |
| CUMPLIÓ / PARCIAL / FALLÓ | Estados de cumplimiento de un **servicio** proyectado frente al real |
| Franjas horarias | NOCTURNA 00–05 · MAÑANA 06–11 · TARDE 12–17 · NOCHE 18–23 |
| Margen de puntualidad | ±10 minutos (tolerancia estándar ya usada en el Excel) |
| Coeficiente operativo | Peso relativo de un móvil dentro del total proyectado de su base, usado para estimar impacto ante faltantes |

---

## 3. Estructura de datos real (extraída directamente de los Excel de la operación)

Esto **no es un modelo inventado** — son las columnas reales de `Seguimiento_Trafico_Local_Abril_2026_FINAL_4.xlsx`, hoja por hoja. La app debe poder importar y/o replicar esta estructura.

### 3.1 `NOMINA_MOV` — nómina planificada
```
BASE | MÓVIL | TIPO MÓVIL | [1 col por día del mes, ej. "1\nMIÉ", "2\nJUE"...]
```
- Cada celda de día contiene `HH:MM-HH:MM` (turno) **o** un código de ausencia (`FCO`, `VAC`, `QRX`, `ENF`, `DOC`).
- Bases observadas: `6001`, `10541`, `13305` (MECA aparece como sub-flota/etiqueta de proyección, ver 3.3).
- `TIPO MÓVIL`: categoría operativa del móvil (ej. `TALLER`).

### 3.2 `IMPORTAR_REAL` — carga cruda de eventos del sistema real
```
FECHA HORA INGRESO | FECHA HORA EGRESO | MÓVIL   (estas 3 se pegan tal cual del export)
BASE | FECHA (día) | HORA INGRESO | HORA EGRESO | ESTADO CRUCE   (calculadas)
```
- **Importante:** esta hoja SÍ tiene ingreso y egreso — es el reporting mensual histórico. El feed en tiempo real de la GAP, en cambio, según lo confirmado con el cliente, solo entrega **primer loguin del día** (sin egreso). La app debe soportar ambos casos: modelo de datos con `hora_ingreso`/`hora_egreso` opcionales, alimentado en tiempo real solo con ingreso, y completable retroactivamente vía carga masiva mensual si en el futuro hay egreso disponible.

### 3.3 `DATOS_PROY` / `DATOS_REAL` — proyección y real de servicios, hora a hora
```
ETIQUETA BASE | H (hora 0-23) | [1 col por día del mes, con cantidad de servicios]
```
Etiquetas observadas: `PROY_6001:TRSL_LIV`, `PROY_MECA_6001`, `PROY_10541`, `PROY_13305`
→ Esta es la fuente real para "proyecciones de flota por tipo de servicio" y "análisis de impacto hora a hora" pedidos en el alcance del proyecto. Misma estructura para proyectado (`DATOS_PROY`) y real (`DATOS_REAL`), lo que permite comparar directamente.

### 3.4 `MOVILES_REAL` — cruce planificado vs. real por móvil/día
```
BASE | MÓVIL | FECHA | DÍA | TURNO PLAN | ING PLAN | ING REAL | EGR PLAN | EGR REAL |
ESTADO | DESVÍO ING (min) | DESVÍO EGR (min) | CUMPLE INGRESO | HS TRAB REAL | OBSERVACIONES
```
Esta es la tabla de hechos central: un registro por móvil por día, con desvíos ya calculados en minutos y el estado de cumplimiento. El motor de alertas en tiempo real es, en esencia, una versión "hoy, minuto a minuto" de esta tabla.

### 3.5 `ANÁLISIS` — puntualidad agregada por base
```
BASE | PUNTUALIDAD (%) | TARDÍO (%) | ANTICIPADO (%) | AUSENCIA (%) | DESVÍO PROMEDIO (min)
```

### 3.6 `DASHBOARD_DIARIO` / `DASHBOARD_MENSUAL`
Vistas de cumplimiento por base y por día para las 4 flotas simultáneamente (sin selector/dropdown — visibilidad de todas las bases a la vez, requisito ya validado).

---

## 4. Arquitectura ya definida y validada (no rediseñar desde cero)

Ya se construyó y probó de punta a punta un scaffold funcional. El asistente de GitHub debe **partir de esta arquitectura**, no proponer una nueva:

```
fleet-tracker/
├── backend/          FastAPI + SQLAlchemy (Python 3.12)
│   └── app/
│       ├── api/        auth, flota, alertas, kpis, carga
│       ├── models/     modelos SQLAlchemy + schemas Pydantic
│       ├── services/   gps_provider.py (adaptador), alertas_engine.py
│       └── core/       config, database, security (JWT + bcrypt)
├── frontend/          React + Vite, responsive/PWA (instalable en celu sin app store)
└── docker-compose.yml PostgreSQL + backend + frontend, despliegue on-premise
```

### 4.1 Pieza clave: adaptador GPS intercambiable
Todo el backend habla contra una interfaz `GPSProvider` (`backend/app/services/gps_provider.py`), con dos implementaciones:
- `MockGPSProvider`: datos simulados, en uso hoy porque **no hay acceso a la API de la GAP todavía**.
- `GAPProvider`: esqueleto ya creado, pendiente de completar el día que haya documentación/credenciales. Cambiar una variable de entorno (`GPS_PROVIDER=gap`) activa el proveedor real sin tocar el resto del sistema.

**Instrucción para el asistente:** cualquier feature nueva relacionada a GPS/posición debe consumir `GPSProvider`, nunca llamar a un proveedor específico directamente.

### 4.2 Motor de alertas
`services/alertas_engine.py` compara `ServicioProyectado` (planificación) contra la última `LecturaGPS` (real), y genera `Alerta` con severidad:
- `ADVERTENCIA` a partir de 10 min sin login tras inicio de turno
- `CRÍTICA` a partir de 25 min

Estos umbrales deben quedar configurables (hoy son constantes en el archivo) — alinear con el margen de ±10 min ya usado en el Excel (`ANÁLISIS`) para no introducir un criterio de puntualidad distinto al que ya usa el equipo.

### 4.3 Modelo de datos ya implementado
`BaseDespacho`, `Agente`, `Movil`, `ServicioProyectado`, `LecturaGPS`, `Alerta` — ver sección 3 para mapear contra las columnas reales del Excel al extender el modelo (especialmente para incorporar `IMPORTAR_REAL`/`MOVILES_REAL` como historial).

### 4.4 Backend — endpoints ya construidos
```
POST /api/auth/login
POST /api/flota/sincronizar        # pull desde GPSProvider activo
GET  /api/flota/estado             # estado actual, filtrable por base
POST /api/alertas/evaluar          # corre el motor de reglas
GET  /api/alertas                  # lista alertas activas
PATCH /api/alertas/{id}/justificar # cierra alerta con motivo (FCO/VAC/QRX/ENF/DOC/otro)
GET  /api/kpis/resumen             # cumplimiento por base
GET  /api/kpis/impacto-faltante    # impacto estimado si un móvil falta
POST /api/carga/nomina             # carga masiva Excel
POST /api/carga/planificacion      # carga masiva Excel
```

### 4.5 Sistema de diseño (ya definido — no usar paletas genéricas de IA)
La dirección visual está **anclada en el mundo real del auxilio vial**, no en un dashboard tech genérico:
- Paleta: negro-asfalto cálido (`#16151a`), ámbar de LED de consola de despacho (`#ffb000`) como acento primario, naranja de baliza (`#ff6a13`), rojo ladrillo de peligro (`#d8402a`, no rosa/neón), verde ruta apagado (`#5ec98b`). Sin azul-cian-violeta con glow.
- Tipografía: Barlow Condensed (títulos, misma familia que la cartelería vial) + Share Tech Mono (datos/números, estilo lectura digital de radio de despacho).
- Elemento de firma: franja diagonal amarillo/negro de peligro (la misma librea de las grúas de auxilio) como divisor bajo el header. Indicadores LED cuadrados parpadeantes, no puntos con glow circular. Controles sin border-radius (estética de consola física, no de app).
- Branding: `SOS · Red de Asistencia`.

---

## 5. Alcance funcional completo (lo construido + lo pendiente)

### Ya construido y probado
- [x] Autenticación (JWT)
- [x] Sincronización y estado de flota en vivo (mock GPS)
- [x] Motor de alertas por severidad (ADVERTENCIA/CRÍTICA) con justificación por código de ausencia
- [x] KPIs de cumplimiento por base
- [x] Cálculo de impacto estimado si un móvil falta (`coeficiente_operativo`)
- [x] Carga masiva de nómina y planificación por Excel
- [x] Frontend responsive/PWA con 4 pantallas (Dashboard, Flota en vivo, Alertas, Carga masiva)
- [x] Docker Compose para despliegue on-premise

### Pendiente — priorizar en este orden
1. **Integración real con la GAP** — bloqueado hasta conseguir documentación de API o credenciales. Mientras tanto, todo el desarrollo debe seguir usando `MockGPSProvider`.
2. **Proyecciones por tipo de servicio** (sección 3.3) — importar `DATOS_PROY`/`DATOS_REAL` y exponer comparación proyectado vs. real por base y por hora, replicando la granularidad horaria (0–23h) que ya existe en el Excel.
3. **Análisis de impacto hora a hora** ante faltantes de unidades — extender `GET /api/kpis/impacto-faltante` para proyectar el efecto por franja horaria (NOCTURNA/MAÑANA/TARDE/NOCHE), no solo como número único.
4. **Planificación semanal de turnos editable en la UI** — hoy solo existe carga por Excel; falta una vista de edición/calendario en el frontend.
5. **Historial de indicadores por período** — incorporar la lógica de `MOVILES_REAL` y `ANÁLISIS` (puntualidad, tardío, anticipado, ausencia, desvío promedio) como vista de series históricas, no solo el estado de hoy.
6. **Dashboards con KPIs y gráficos de cumplimiento** — extender el dashboard actual con las vistas equivalentes a `DASHBOARD_DIARIO` y `DASHBOARD_MENSUAL`.
7. **Administración de móviles y agentes vinculados a identificadores GPS** — CRUD completo en la UI (hoy la carga es solo vía Excel).
8. **Sistema de usuarios con roles** — hoy hay un único usuario demo hardcodeado.
9. **Notificaciones push para alertas críticas.**

---

## 6. Restricciones técnicas no negociables

- **Compatibilidad LibreOffice** en cualquier exportación/plantilla Excel que la app genere (el equipo abre estos archivos con LibreOffice, no solo Excel) — evitar fórmulas AGGREGATE con arrays; usar INDEX/MATCH con claves concatenadas si se generan plantillas descargables.
- **Terminología exacta** del glosario (sección 2) en variables, endpoints, y UI — no traducir ni sinonimizar (ej. no usar "conductor" en vez de "agente").
- **Todas las 4 bases visibles simultáneamente** por defecto — nunca ocultar bases detrás de un selector como vista por defecto.
- **El feed en tiempo real no tiene egreso** — no asumir datos de logout en ninguna pantalla que consuma datos "en vivo"; el egreso solo existe en el histórico mensual cargado manualmente.
- **On-premise**: la app corre en servidor propio de la empresa vía Docker Compose, no asumir infraestructura cloud gestionada.

---

## 7. Cómo usar este documento

Pegar este archivo completo como descripción inicial de un issue o como prompt de Copilot Workspace, junto con el repositorio ya scaffoldeado (`fleet-tracker.zip` ya entregado, con 3 commits de historial). Pedirle al asistente que trabaje **un ítem de la sección 5 a la vez**, en el orden priorizado, respetando la arquitectura de la sección 4 y el glosario de la sección 2.
