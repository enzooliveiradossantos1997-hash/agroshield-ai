"""
AgroShield AI — Fail-Safe Zero-Failure & 72h Predictive Forecast Test Suite
Author: Enzo Oliveira dos Santos
Field: Verification of Industrial Security Headers, Dual-Consensus Safety, and 72h Forecasting
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from fastapi.testclient import TestClient
from src.api.main import app, load_artifacts


class TestFailSafeAndForecast(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_artifacts()
        cls.client = TestClient(app)

    def test_01_enterprise_security_headers_injection(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(response.headers.get("x-frame-options"), "DENY")
        self.assertIn("Verified-ASAE-D245.5", response.headers.get("x-agroshield-integrity", ""))

    def test_02_predictive_72h_window_endpoint(self):
        response = self.client.get("/api/v1/forecast/72h-window?county=story_county_ia")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["county_hub"], "story_county_ia")
        self.assertGreaterEqual(len(data["hourly_telemetry"]), 24)
        self.assertIn("safety_confidence_score", data)
        self.assertGreaterEqual(data["safety_confidence_score"], 0.95)

        # Check hourly point data structure
        first_hour = data["hourly_telemetry"][0]
        self.assertIn("temperature_c", first_hour)
        self.assertIn("relative_humidity_pct", first_hour)
        self.assertIn("emc_corn_wet_basis", first_hour)
        self.assertIn("recommended_relay_state", first_hour)

    def test_03_fail_safe_security_audit_endpoint(self):
        response = self.client.get("/api/v1/security/fail-safe-audit")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Fail-Safe Deterministic Lockout", data["assurance_protocol"])
        self.assertTrue(data["defense_in_depth"]["hsts_enforced"])
        self.assertTrue(data["defense_in_depth"]["boundary_rejection_http_422"])
        self.assertEqual(data["audited_by"], "Enzo Oliveira dos Santos")


if __name__ == "__main__":
    unittest.main()
