"""
AgroShield AI — Edge Computing & Chaos Engineering Resilience Test Suite
Author: Enzo Oliveira dos Santos
Field: Verification of Offline-First Autonomous Operation & Store-and-Forward Recovery
"""

import sys
import os
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from fastapi.testclient import TestClient
from src.api.main import app, load_artifacts
from src.edge.local_controller import LocalEdgeGateway
from src.edge.schemas import BinSensorTelemetryFrame, SensorCableReading


class TestEdgeResilience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_artifacts()
        cls.client = TestClient(app)

    def setUp(self):
        # Create temporary isolated SQLite database for clean edge testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.gateway = LocalEdgeGateway(db_path=self.temp_db.name)

    def tearDown(self):
        try:
            if os.path.exists(self.temp_db.name):
                os.remove(self.temp_db.name)
        except Exception:
            pass

    def _sample_frame(self, ambient_rh: float = 85.0) -> BinSensorTelemetryFrame:
        return BinSensorTelemetryFrame(
            bin_id="BIN-IOWA-CHAOS-01",
            crop_type="corn",
            ambient_temp_c=4.0,
            ambient_rh_pct=ambient_rh,
            headspace_temp_c=5.0,
            average_grain_temp_c=22.0,
            average_grain_moisture_pct=14.0,
            sensor_depth_profile=[
                SensorCableReading(sensor_index=0, depth_meters=1.0, temperature_c=18.0, moisture_pct=13.8),
                SensorCableReading(sensor_index=1, depth_meters=3.0, temperature_c=22.0, moisture_pct=14.1),
                SensorCableReading(sensor_index=2, depth_meters=5.0, temperature_c=24.0, moisture_pct=14.2),
            ]
        )

    def test_01_local_agrophysics_evaluation_online(self):
        frame = self._sample_frame(ambient_rh=85.0)
        decision = self.gateway.evaluate_local_frame(frame)
        self.assertEqual(decision.connectivity_mode, "CLOUD_ONLINE")
        self.assertEqual(decision.local_relay_command, "FAN_RELAY_LOCKOUT")
        self.assertTrue(decision.is_synced_to_cloud)

    def test_02_chaos_network_blackout_offline_autonomy(self):
        # SIMULATE CHAOS: Rural satellite/cell tower complete failure
        self.gateway.set_network_blackout_simulation(True)

        frame = self._sample_frame(ambient_rh=88.0)
        decision = self.gateway.evaluate_local_frame(frame)

        # Autonomous Edge Mode Activated
        self.assertEqual(decision.connectivity_mode, "OFFLINE_EDGE_AUTONOMOUS")
        # Physical hardware safety lock engaged locally without cloud dependency
        self.assertEqual(decision.local_relay_command, "FAN_RELAY_LOCKOUT")
        self.assertFalse(decision.is_synced_to_cloud)

        # Telemetry safely stored in local WAL SQLite queue
        pending_count = self.gateway.get_pending_offline_count()
        self.assertGreaterEqual(pending_count, 1)

    def test_03_store_and_forward_recovery_zero_data_loss(self):
        # 1. Enqueue 3 frames during blackout
        self.gateway.set_network_blackout_simulation(True)
        for i in range(3):
            self.gateway.evaluate_local_frame(self._sample_frame())

        self.assertEqual(self.gateway.get_pending_offline_count(), 3)

        # 2. RESTORE NETWORK (Internet reconnects)
        self.gateway.set_network_blackout_simulation(False)

        # 3. Flush offline backlog to Cloud
        flushed = self.gateway.flush_offline_backlog()
        self.assertEqual(flushed, 3)
        self.assertEqual(self.gateway.get_pending_offline_count(), 0)

    def test_04_cloud_sync_batch_endpoint(self):
        batch = [
            {"bin_id": "BIN-01", "timestamp_utc": "2026-09-29T18:00:00Z", "relay": "FAN_RELAY_LOCKOUT"},
            {"bin_id": "BIN-02", "timestamp_utc": "2026-09-29T18:01:00Z", "relay": "FAN_RELAY_ON_STAGE_1"}
        ]
        res = self.client.post("/api/v1/telemetry/sync-batch", json=batch)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["ingested_count"], 2)


if __name__ == "__main__":
    unittest.main()
