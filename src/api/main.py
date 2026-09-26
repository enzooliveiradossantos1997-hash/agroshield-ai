from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="AgroShield AI – Climate Risk API",
    description="Baseline API for climate risk prediction and agribusiness decision support.",
    version="0.1.0",
)


@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "service": "AgroShield AI",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/")
def root():
    return {
        "message": "AgroShield AI API is running. See /docs for interactive documentation."
    }
