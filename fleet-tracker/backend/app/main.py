from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import init_db, SessionLocal
from app.api import auth, flota, alertas, kpis, carga
from app.services.alertas_engine import evaluar_flota

app = FastAPI(title="Seguimiento de Flota en Tiempo Real")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restringir a la URL del frontend en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(flota.router)
app.include_router(alertas.router)
app.include_router(kpis.router)
app.include_router(carga.router)


@app.on_event("startup")
def startup():
    init_db()

    # Job en segundo plano: sincroniza GPS y evalúa alertas cada 2 minutos.
    scheduler = BackgroundScheduler()

    def ciclo():
        db = SessionLocal()
        try:
            evaluar_flota(db)
        finally:
            db.close()

    scheduler.add_job(ciclo, "interval", minutes=2)
    scheduler.start()


@app.get("/api/health")
def health():
    return {"status": "ok"}
