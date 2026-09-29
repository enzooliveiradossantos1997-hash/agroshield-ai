"""
AgroShield AI — Edge Gateway Data Contracts
Author: Enzo Oliveira dos Santos
Field: Industrial IoT & High-Reliability Edge Computing
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class SensorCableReading(BaseModel):
    sensor_index: int = Field(..., description="Depth index of temperature sensor (0=Bottom, 4=Surface)")
    depth_meters: float
    temperature_c: float
    moisture_pct: float


class BinSensorTelemetryFrame(BaseModel):
    bin_id: str = Field(..., examples=["BIN-IOWA-042"])
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    crop_type: Literal["corn", "soybeans"] = "corn"
    ambient_temp_c: float
    ambient_rh_pct: float
    headspace_temp_c: float
    average_grain_temp_c: float
    average_grain_moisture_pct: float
    sensor_depth_profile: List[SensorCableReading] = Field(default_factory=list)


class EdgeDecisionFrame(BaseModel):
    bin_id: str
    timestamp_utc: str
    connectivity_mode: Literal["CLOUD_ONLINE", "OFFLINE_EDGE_AUTONOMOUS"]
    calculated_emc_pct: float
    thermal_gradient_c: float
    local_relay_command: Literal[
        "FAN_RELAY_LOCKOUT",
        "FAN_RELAY_ON_STAGE_1",
        "FAN_RELAY_ON_STAGE_2",
        "FAN_RELAY_OFF"
    ]
    headspace_exhaust_active: bool
    fail_safe_reason: str
    is_synced_to_cloud: bool
