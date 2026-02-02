from fastapi import FastAPI
from app.database import engine, Base
from app import models

from app.api import assets, auditor

# Create database tables on startup (Simple approach for initialization)
# In production, we would use Alembic for migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(title="KlyrSignals API", version="0.1.0")

app.include_router(assets.router)
app.include_router(auditor.router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "KlyrSignals Backend"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
