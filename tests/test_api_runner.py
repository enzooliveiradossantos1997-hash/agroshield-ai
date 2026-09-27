"""
AgroShield AI — Automated Production Test Suite (Standard Library Unittest)
Author: Enzo Oliveira dos Santos
Field: Production-Grade Quality Assurance & Verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from fastapi.testclient import TestClient
from src.api.main import app, load_artifacts
from src.models.emc import calculate_emc, evaluate_aeration_suitability, evaluate_condensation_risk


class TestAgroShieldAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Explicitly initialize artifacts for test runner
        load_artifacts()
        cls.client = TestClient(app)

    def test_01_healthcheck(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "AgroShield AI")
        self.assertIn(data["model_status"], ["active", "fallback_deterministic"])

    def test_02_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["author"], "Enzo Oliveira dos Santos")
        self.assertEqual(data["version"], "1.0.0")

    def test_03_emc_calculation_corn_and_soybeans(self):
        # Corn EMC (Dry Basis) at 75% RH and 15°C is approx 19.2%
        emc_corn = calculate_emc(75.0, 15.0, "corn")
        self.assertTrue(16.0 <= emc_corn <= 22.0, f"Corn EMC out of bounds: {emc_corn}")

        # At lower humidity (55% RH), Corn EMC drops to safe storage range (~13-16%)
        emc_corn_dry = calculate_emc(55.0, 15.0, "corn")
        self.assertTrue(12.0 <= emc_corn_dry <= 16.5, f"Corn Dry EMC out of bounds: {emc_corn_dry}")

        # Soybeans equilibrium at 75% RH and 15°C
        emc_soy = calculate_emc(75.0, 15.0, "soybeans")
        self.assertTrue(13.0 <= emc_soy <= 18.0, f"Soy EMC out of bounds: {emc_soy}")

    def test_04_predict_storage_risk_safe(self):
        payload = {
            "crop_type": "corn",
            "grain_temp_c": 12.0,
            "grain_moisture_pct": 13.0,
            "ambient_temp_c": 10.0,
            "ambient_rh_pct": 60.0,
            "days_in_storage": 45
        }
        response = self.client.post("/api/v1/predict/storage-risk", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["risk_level_code"], [0, 1])
        self.assertGreaterEqual(data["confidence_score"], 0.70)
        self.assertIn("calculated_emc_pct", data)

    def test_05_predict_storage_risk_critical(self):
        payload = {
            "crop_type": "corn",
            "grain_temp_c": 28.0,
            "grain_moisture_pct": 18.5,
            "ambient_temp_c": 5.0,
            "ambient_rh_pct": 85.0,
            "days_in_storage": 10
        }
        response = self.client.post("/api/v1/predict/storage-risk", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["risk_level_code"], 2)
        self.assertIn("CRITICAL", data["risk_level_label"])

    def test_06_physical_boundary_rejection_security(self):
        # Invalid RH > 100% and extreme temp must return HTTP 422 Unprocessable Entity
        invalid_payload = {
            "crop_type": "corn",
            "grain_temp_c": 120.0,
            "grain_moisture_pct": 13.0,
            "ambient_temp_c": 10.0,
            "ambient_rh_pct": 150.0,
            "days_in_storage": 45
        }
        response = self.client.post("/api/v1/predict/storage-risk", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_07_condensation_alert_endpoint(self):
        payload = {
            "grain_temp_c": 22.0,
            "grain_moisture_pct": 15.0,
            "forecast_min_temp_c": -5.0,
            "silo_type": "corrugated_steel"
        }
        response = self.client.post("/api/v1/predict/condensation-alert", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["condensation_risk_level"], 2)
        self.assertTrue(data["roof_condensation_danger"])

    def test_08_model_metadata_endpoint(self):
        response = self.client.get("/api/v1/model/metadata")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["model_type"], "RandomForestClassifier")
        self.assertGreaterEqual(data["accuracy_pct"], 95.0)
        self.assertEqual(data["training_metadata"]["author"], "Enzo Oliveira dos Santos")


if __name__ == "__main__":
    unittest.main()
