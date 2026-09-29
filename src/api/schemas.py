"""
AgroShield AI — Strict Pydantic Validation Schemas
Author: Enzo Oliveira dos Santos
Field: Production-Grade Security & Physical Boundary Enforcement
"""

from typing import Literal, Dict, Any, List, Optional
from pydantic import BaseModel, Field


class GrainTelemetryInput(BaseModel):
    crop_type: Literal["corn", "soybeans"] = Field(
        default="corn",
        description="Type of grain stored: 'corn' or 'soybeans'"
    )
    grain_temp_c: float = Field(
        ...,
        ge=-20.0,
        le=55.0,
        description="Internal grain bulk temperature in Celsius (-20°C to 55°C)",
        examples=[18.5]
    )
    grain_moisture_pct: float = Field(
        ...,
        ge=5.0,
        le=35.0,
        description="Current grain moisture content percentage (5% to 35%)",
        examples=[15.2]
    )
    ambient_temp_c: float = Field(
        ...,
        ge=-45.0,
        le=55.0,
        description="Outside ambient air temperature in Celsius from NOAA weather station (-45°C to 55°C)",
        examples=[2.0]
    )
    ambient_rh_pct: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Outside ambient relative humidity percentage (0% to 100%)",
        examples=[75.0]
    )
    days_in_storage: int = Field(
        default=30,
        ge=1,
        le=730,
        description="Number of days the grain has been in the storage bin",
        examples=[45]
    )


class SiloRiskPredictionResponse(BaseModel):
    risk_level_code: int = Field(..., description="0 = Safe, 1 = Warning (Aerate), 2 = Critical (Mold/Spoilage)")
    risk_level_label: str = Field(..., description="Human-readable risk category")
    confidence_score: float = Field(..., description="Model prediction probability (0.0 to 1.0)")
    calculated_emc_pct: float = Field(..., description="Equilibrium Moisture Content calculated via Henderson-Thompson")
    temp_gradient_c: float = Field(..., description="Difference between grain temperature and outside air (grain - ambient)")
    aeration_recommendation: str = Field(..., description="Operational fan action: AERATE_COOLING, AERATE_DRYING, DO_NOT_AERATE, HOLD_EQUILIBRIUM")
    action_narrative: str = Field(..., description="Detailed agronomic guidance for farm manager")
    fallback_mode: bool = Field(default=False, description="True if graceful degradation fallback was used")
    timestamp_utc: str


class CondensationAlertInput(BaseModel):
    grain_temp_c: float = Field(..., ge=-20.0, le=55.0)
    grain_moisture_pct: float = Field(..., ge=5.0, le=35.0)
    forecast_min_temp_c: float = Field(..., ge=-45.0, le=50.0, description="Forecasted overnight minimum ambient temperature")
    silo_type: Literal["corrugated_steel", "concrete"] = Field(default="corrugated_steel")


class CondensationAlertResponse(BaseModel):
    condensation_risk_level: int = Field(..., description="0 = Safe, 1 = Moderate, 2 = Severe")
    risk_summary: str
    thermal_gradient_c: float
    roof_condensation_danger: bool
    recommended_mitigation: str
    timestamp_utc: str


class CountyWeatherResponse(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    current_temp_c: float
    current_rh_pct: float
    dew_point_c: float
    forecast_min_overnight_c: float
    source: str
    is_fallback: bool
    timestamp_utc: str


class AutonomousAdvisoryInput(BaseModel):
    crop_type: Literal["corn", "soybeans"] = Field(
        default="corn",
        description="Type of grain: 'corn' or 'soybeans'"
    )
    grain_temp_c: float = Field(
        ...,
        ge=-20.0,
        le=55.0,
        description="Internal grain temperature measured by silo sensor cable (°C)",
        examples=[19.0]
    )
    grain_moisture_pct: float = Field(
        ...,
        ge=5.0,
        le=35.0,
        description="Grain moisture tester percentage (5% to 35%)",
        examples=[15.8]
    )
    county_hub: Literal[
        "story_county_ia",
        "polk_county_ia",
        "mclean_county_il",
        "york_county_ne",
        "kandiyohi_county_mn",
        "custom_coordinates"
    ] = Field(
        default="story_county_ia",
        description="Preset US Corn Belt county hub or custom coordinates"
    )
    custom_lat: Optional[float] = Field(default=None, ge=24.0, le=50.0, description="Optional custom latitude in continental US")
    custom_lon: Optional[float] = Field(default=None, ge=-125.0, le=-66.0, description="Optional custom longitude in continental US")
    days_in_storage: int = Field(default=30, ge=1, le=730)


class AutonomousAdvisoryResponse(BaseModel):
    crop_type: str
    location: str
    live_ambient_temp_c: float
    live_ambient_rh_pct: float
    overnight_min_forecast_c: float
    calculated_emc_pct: float
    thermal_gradient_c: float
    risk_level_code: int
    risk_level_label: str
    aeration_recommendation: str
    aeration_relay_command: Literal["FAN_RELAY_OFF", "FAN_RELAY_ON_STAGE_1", "FAN_RELAY_ON_STAGE_2", "FAN_RELAY_LOCKOUT"]
    condensation_hazard: bool
    operational_action_plan: str
    weather_source: str
    is_telemetry_fallback: bool
    timestamp_utc: str

