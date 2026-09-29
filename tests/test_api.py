"""
AgroShield AI — Automated Test Suite (Pytest)
Author: Enzo Oliveira dos Santos
Field: Production-Grade Quality Assurance & CI/CD
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app, load_artifacts
from src.models.emc import calculate_emc, evaluate_aeration_suitability, evaluate_condensation_risk

# Initialize model and metrics for test runner
load_artifacts()
client = TestClient(app)


def test_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AgroShield AI"
    assert data["model_status"] in ["active", "fallback_deterministic"]


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["author"] == "Enzo Oliveira dos Santos"
    assert data["version"] == "1.0.0"


def test_emc_calculation_corn_and_soybeans():
    # At 75% RH and 15°C, corn dry basis EMC is approx 19.2%
    emc_corn = calculate_emc(75.0, 15.0, "corn")
    assert 16.0 <= emc_corn <= 22.0
    
    # Soybeans equilibrium dry basis
    emc_soy = calculate_emc(75.0, 15.0, "soybeans")
    assert 13.0 <= emc_soy <= 18.0



def test_predict_storage_risk_safe():
    # Safe storage conditions: Dry corn, low temperature gradient
    payload = {
        "crop_type": "corn",
        "grain_temp_c": 12.0,
        "grain_moisture_pct": 13.0,
        "ambient_temp_c": 10.0,
        "ambient_rh_pct": 60.0,
        "days_in_storage": 45
    }
    response = client.post("/api/v1/predict/storage-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level_code"] in [0, 1]
    assert "confidence_score" in data
    assert "calculated_emc_pct" in data


def test_predict_storage_risk_critical():
    # Dangerous conditions: Wet grain with severe thermal shock
    payload = {
        "crop_type": "corn",
        "grain_temp_c": 28.0,
        "grain_moisture_pct": 18.5,
        "ambient_temp_c": 5.0,
        "ambient_rh_pct": 85.0,
        "days_in_storage": 10
    }
    response = client.post("/api/v1/predict/storage-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level_code"] == 2
    assert "CRITICAL" in data["risk_level_label"]


def test_physical_boundary_rejection_security():
    # Invalid physical values (e.g. humidity > 100% or moisture < 0) must be rejected by Pydantic with 422
    invalid_payload = {
        "crop_type": "corn",
        "grain_temp_c": 120.0,  # Impossible grain temp
        "grain_moisture_pct": 13.0,
        "ambient_temp_c": 10.0,
        "ambient_rh_pct": 150.0,  # Invalid RH > 100%
        "days_in_storage": 45
    }
    response = client.post("/api/v1/predict/storage-risk", json=invalid_payload)
    assert response.status_code == 422


def test_condensation_alert_endpoint():
    payload = {
        "grain_temp_c": 22.0,
        "grain_moisture_pct": 15.0,
        "forecast_min_temp_c": -5.0,
        "silo_type": "corrugated_steel"
    }
    response = client.post("/api/v1/predict/condensation-alert", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["condensation_risk_level"] == 2
    assert data["roof_condensation_danger"] is True


def test_model_metadata_endpoint():
    response = client.get("/api/v1/model/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["model_type"] == "RandomForestClassifier"
    assert data["accuracy_pct"] >= 95.0
