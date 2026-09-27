"""
AgroShield AI — Climate Risk & Grain Storage Preservation API
Author: Enzo Oliveira dos Santos
Field: Production-Grade Agritech Microservice

Integrates Henderson-Thompson Equilibrium Moisture Content (EMC) agrophysics
with a trained Scikit-Learn Random Forest model for grain loss mitigation in US storage bins.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np

from src.api.schemas import (
    GrainTelemetryInput,
    SiloRiskPredictionResponse,
    CondensationAlertInput,
    CondensationAlertResponse,
)
from src.models.emc import (
    calculate_emc,
    evaluate_aeration_suitability,
    evaluate_condensation_risk,
)

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AgroShield-AI] %(message)s"
)
logger = logging.getLogger("agroshield-api")

app = FastAPI(
    title="AgroShield AI — Silo Preservation & Climate Risk Engine",
    description=(
        "Production AI system by Enzo Oliveira dos Santos designed to mitigate post-harvest "
        "grain losses, thermal shock condensation, and mycotoxin spoilage across the US Midwest Corn Belt."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security: CORS Middleware configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global model state
MODEL = None
METRICS: Dict[str, Any] = {}
RISK_LABELS = {
    0: "SAFE (Optimal Equilibrium)",
    1: "WARNING (Aeration Recommended - Respiration/Moisture)",
    2: "CRITICAL (Immediate Action - Thermal Shock / Mold Danger)"
}

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/artifacts/spoilage_model.joblib"))
METRICS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/artifacts/model_metrics.json"))


@app.on_event("startup")
def load_artifacts():
    global MODEL, METRICS
    logger.info("Initializing AgroShield AI engine artifacts...")
    
    if os.path.exists(MODEL_PATH):
        try:
            MODEL = joblib.load(MODEL_PATH)
            logger.info("Scikit-Learn ensemble model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model artifact: {e}. Graceful fallback active.")
            MODEL = None
    else:
        logger.warning(f"Model artifact not found at {MODEL_PATH}. Graceful fallback active.")

    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                METRICS = json.load(f)
            logger.info("Model metrics loaded.")
        except Exception as e:
            logger.warning(f"Could not load metrics: {e}")


@app.get("/", tags=["System"])
def root():
    return {
        "service": "AgroShield AI",
        "author": "Enzo Oliveira dos Santos",
        "description": "Climate risk prediction and grain storage preservation API",
        "documentation": "/docs",
        "version": "1.0.0",
        "model_loaded": MODEL is not None
    }


@app.get("/health", tags=["System"])
def healthcheck():
    return {
        "status": "healthy",
        "service": "AgroShield AI",
        "engine": "Henderson-Thompson EMC + Scikit-Learn RF",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model_status": "active" if MODEL is not None else "fallback_deterministic"
    }


@app.post(
    "/api/v1/predict/storage-risk",
    response_model=SiloRiskPredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction & Decision Support"]
)
def predict_storage_risk(telemetry: GrainTelemetryInput):
    """
    Predicts grain spoilage risk using physical parameters (grain temperature, moisture,
    ambient NOAA air conditions, and calculated Henderson-Thompson EMC).
    """
    crop = telemetry.crop_type.lower()
    crop_code = 0 if crop == "corn" else 1
    
    # 1. Agrophysical evaluation (Henderson-Thompson)
    aeration_info = evaluate_aeration_suitability(
        ambient_temp_c=telemetry.ambient_temp_c,
        ambient_rh_pct=telemetry.ambient_rh_pct,
        grain_temp_c=telemetry.grain_temp_c,
        grain_moisture_pct=telemetry.grain_moisture_pct,
        crop=crop
    )
    
    emc = aeration_info["calculated_emc_pct"]
    temp_grad = telemetry.grain_temp_c - telemetry.ambient_temp_c
    
    # 2. Machine Learning Inference with Graceful Degradation
    fallback_used = False
    if MODEL is not None:
        try:
            import pandas as pd
            features_df = pd.DataFrame([{
                "crop_code": crop_code,
                "grain_temp_c": telemetry.grain_temp_c,
                "grain_moisture_pct": telemetry.grain_moisture_pct,
                "ambient_temp_c": telemetry.ambient_temp_c,
                "ambient_rh_pct": telemetry.ambient_rh_pct,
                "days_in_storage": telemetry.days_in_storage,
                "emc_pct": emc,
                "temp_gradient_c": temp_grad
            }])
            
            risk_code = int(MODEL.predict(features_df)[0])
            probabilities = MODEL.predict_proba(features_df)[0]
            confidence = float(probabilities[risk_code])
        except Exception as e:
            logger.error(f"Inference error: {e}. Executing deterministic fallback.")
            fallback_used = True
            risk_code = 2 if (temp_grad >= 14 or telemetry.grain_moisture_pct >= 16) else (1 if temp_grad >= 8 or telemetry.grain_moisture_pct >= 14 else 0)
            confidence = 0.90
    else:
        fallback_used = True
        risk_code = 2 if (temp_grad >= 14 or telemetry.grain_moisture_pct >= 16) else (1 if temp_grad >= 8 or telemetry.grain_moisture_pct >= 14 else 0)
        confidence = 0.88

    return SiloRiskPredictionResponse(
        risk_level_code=risk_code,
        risk_level_label=RISK_LABELS.get(risk_code, "UNKNOWN"),
        confidence_score=round(confidence, 4),
        calculated_emc_pct=emc,
        temp_gradient_c=round(temp_grad, 1),
        aeration_recommendation=aeration_info["aeration_recommendation"],
        action_narrative=aeration_info["agronomic_reason"],
        fallback_mode=fallback_used,
        timestamp_utc=datetime.now(timezone.utc).isoformat()
    )


@app.post(
    "/api/v1/predict/condensation-alert",
    response_model=CondensationAlertResponse,
    status_code=status.HTTP_200_OK,
    tags=["Prediction & Decision Support"]
)
def predict_condensation_alert(alert_input: CondensationAlertInput):
    """
    Evaluates condensation danger on bin roof steel caused by sudden overnight cold fronts.
    """
    risk_level, summary = evaluate_condensation_risk(
        grain_temp_c=alert_input.grain_temp_c,
        grain_moisture_pct=alert_input.grain_moisture_pct,
        ambient_temp_c=alert_input.forecast_min_temp_c
    )
    
    gradient = alert_input.grain_temp_c - alert_input.forecast_min_temp_c
    
    if risk_level == 2:
        mitigation = "Activate headspace exhaust fans immediately prior to sunset to equalize temperature before dew point is reached."
    elif risk_level == 1:
        mitigation = "Monitor roof condensation sensors. Schedule aeration during lowest humidity hours."
    else:
        mitigation = "Thermal gradient within safe limits. No action required."
        
    return CondensationAlertResponse(
        condensation_risk_level=risk_level,
        risk_summary=summary,
        thermal_gradient_c=round(gradient, 1),
        roof_condensation_danger=risk_level >= 1,
        recommended_mitigation=mitigation,
        timestamp_utc=datetime.now(timezone.utc).isoformat()
    )


@app.get("/api/v1/model/metadata", tags=["Model Auditing & Governance"])
def get_model_metadata():
    """
    Returns transparency and performance metrics for the trained model.
    Used for technical due diligence, auditing, and visa evidence exhibits.
    """
    if not METRICS:
        return {
            "status": "pending_training",
            "message": "Model metrics file is being generated."
        }
    return METRICS
