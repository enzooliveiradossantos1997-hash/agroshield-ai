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
