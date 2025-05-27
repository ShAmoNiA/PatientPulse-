import uvicorn
from fastapi import FastAPI

from app.analytics.run_hourly_analytics import run_hourly_analytics
from app.api import patients, biometrics
from app.analytics.compute import run_etl
from apscheduler.schedulers.background import BackgroundScheduler

def create_tables():
    from app.db.models import Base
    from app.db.session import engine
    Base.metadata.create_all(bind=engine)

app = FastAPI(title="HealthAPI")

@app.on_event("startup")
async def on_startup():
    create_tables()
    run_etl()
    create_tables()

app.include_router(patients.router, prefix="/api/v1")
app.include_router(biometrics.router, prefix="/api/v1")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_hourly_analytics, 'cron', second=10)
    scheduler.start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)