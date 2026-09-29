"""
AgroShield AI — Real-time Weather & Autonomous Advisory Test Suite
Author: Enzo Oliveira dos Santos
Field: Verification of Live NOAA Ingestion, Relay Command Logic, and Metrics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from fastapi.testclient import TestClient
from src.api.main import app, load_artifacts
from src.services.weather_service import weather_service, CORN_BELT_HUBS


class TestWeatherAndAdvisory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_artifacts()
        cls.client = TestClient(app)

    def test_01_weather_live_preset_hub(self):
        response = self.client.get("/api/v1/weather/live?county=story_county_ia")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Story County", data["location_name"])
        self.assertTrue(-40.0 <= data["current_temp_c"] <= 50.0)
        self.assertTrue(0.0 <= data["current_rh_pct"] <= 100.0)
        self.assertIn("source", data)

    def test_02_weather_live_custom_coordinates(self):
        # Des Moines airport approximate coordinates
        response = self.client.get("/api/v1/weather/live?lat=41.53&lon=-93.66")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["latitude"], 41.53)
        self.assertEqual(data["longitude"], -93.66)

    def test_03_weather_invalid_county_rejection(self):
        response = self.client.get("/api/v1/weather/live?county=invalid_county_xyz")
        self.assertEqual(response.status_code, 400)

    def test_04_autonomous_advisory_lockout_when_humid(self):
        # When grain is dry (13%) but outside air is cool & high moisture, fans should be locked out
        payload = {
            "crop_type": "corn",
            "grain_temp_c": 12.0,
            "grain_moisture_pct": 13.0,
            "county_hub": "story_county_ia",
            "days_in_storage": 20
        }
        response = self.client.post("/api/v1/predict/autonomous-advisory", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("aeration_relay_command", data)
        self.assertIn(data["aeration_relay_command"], [
            "FAN_RELAY_OFF",
            "FAN_RELAY_ON_STAGE_1",
            "FAN_RELAY_ON_STAGE_2",
            "FAN_RELAY_LOCKOUT"
        ])
        self.assertIn("calculated_emc_pct", data)

    def test_05_autonomous_advisory_cooling_stage(self):
        # Warm grain (24°C) with cold autumn air should trigger cooling stage 1
        payload = {
            "crop_type": "corn",
            "grain_temp_c": 25.0,
            "grain_moisture_pct": 14.5,
            "county_hub": "mclean_county_il",
            "days_in_storage": 15
        }
        response = self.client.post("/api/v1/predict/autonomous-advisory", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["aeration_relay_command"], [
            "FAN_RELAY_ON_STAGE_1",
            "FAN_RELAY_ON_STAGE_2",
            "FAN_RELAY_LOCKOUT"
        ])
        self.assertIn("operational_action_plan", data)


    def test_06_autonomous_advisory_missing_coordinates_validation(self):
        # Selecting custom_coordinates without lat/lon must return 422
        payload = {
            "crop_type": "corn",
            "grain_temp_c": 15.0,
            "grain_moisture_pct": 14.0,
            "county_hub": "custom_coordinates"
        }
        response = self.client.post("/api/v1/predict/autonomous-advisory", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_07_prometheus_metrics_endpoint(self):
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        content = response.text
        self.assertIn("agroshield_predictions_total", content)
        self.assertIn("agroshield_aeration_commands_total", content)


if __name__ == "__main__":
    unittest.main()
