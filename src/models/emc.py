"""
AgroShield AI — Henderson-Thompson Equilibrium Moisture Content (EMC) Engine
Author: Enzo Oliveira dos Santos
Field: Agricultural Software Engineering & Post-Harvest Risk Mitigation

Mathematical reference:
ASAE Standards D245.5: Moisture Relationships of Plant-based Agricultural Products.
Iowa State University Extension: Grain Drying and Storage EMC Tables.
"""

import math
from typing import Dict, Tuple

# ASAE Standard D245.5 Constants for Modified Henderson-Thompson Equation
# T in Celsius, RH in decimal (0.0 to 1.0), M in Dry Basis %
EMC_CONSTANTS = {
    "corn": {
        "K": 8.6541e-5,
        "C": 49.810,
        "N": 1.8634,
        "safe_moisture_max": 14.0,  # Max safe moisture % for long-term storage
        "safe_temp_max_c": 15.0,    # Target temperature for winter aerated storage
    },
    "soybeans": {
        "K": 1.1172e-4,
        "C": 91.560,
        "N": 1.7010,
        "safe_moisture_max": 13.0,
        "safe_temp_max_c": 15.0,
    }
}


def calculate_emc(
    relative_humidity_pct: float,
    temperature_c: float,
    crop: str = "corn",
    wet_basis: bool = False
) -> float:
    """
    Calculates Equilibrium Moisture Content (EMC) using the modified Henderson-Thompson equation.
    
    Formula:
        M_dry = [ -ln(1 - RH) / (K * (T + C)) ] ^ (1 / N)
        M_wet = M_dry / (1 + M_dry / 100)
    """
    crop_lower = crop.lower()
    if crop_lower not in EMC_CONSTANTS:
        raise ValueError(f"Unsupported crop '{crop}'. Supported: {list(EMC_CONSTANTS.keys())}")
    
    params = EMC_CONSTANTS[crop_lower]
    
    # Boundary sanitation
    rh_decimal = max(0.01, min(0.99, relative_humidity_pct / 100.0))
    temp_adjusted = max(-15.0, min(50.0, temperature_c))
    
    numerator = -math.log(1.0 - rh_decimal)
    denominator = params["K"] * (temp_adjusted + params["C"])
    
    if denominator <= 0:
        return 14.0
        
    m_dry = math.pow(numerator / denominator, 1.0 / params["N"])
    
    if wet_basis:
        m_wet = m_dry / (1.0 + m_dry / 100.0)
        return round(m_wet, 2)
        
    return round(m_dry, 2)


def evaluate_aeration_suitability(
    ambient_temp_c: float,
    ambient_rh_pct: float,
    grain_temp_c: float,
    grain_moisture_pct: float,
    crop: str = "corn"
) -> Dict[str, any]:
    """
    Evaluates whether turning on silo aeration fans will dry, cool, or wet the grain.
    Protects against aeration in humid weather which adds moisture to dry grain mass.
    """
    # Use wet-basis EMC for direct comparison with grain moisture testers
    target_emc = calculate_emc(ambient_rh_pct, ambient_temp_c, crop, wet_basis=True)
    temp_diff = grain_temp_c - ambient_temp_c
    
    # Aeration Decision Matrix
    can_cool = temp_diff >= 5.0
    will_wet_grain = target_emc > grain_moisture_pct + 0.8
    will_dry_grain = target_emc < grain_moisture_pct - 0.5
    
    if will_wet_grain:
        recommendation = "DO_NOT_AERATE"
        reason = f"Outside air RH ({ambient_rh_pct}%) would re-wet grain (EMC {target_emc}% > Grain {grain_moisture_pct}%)."
    elif can_cool:
        recommendation = "AERATE_COOLING"
        reason = f"Optimal cooling window. Grain is {temp_diff:.1f}°C warmer than outside air."
    elif will_dry_grain and grain_moisture_pct > EMC_CONSTANTS[crop.lower()]["safe_moisture_max"]:
        recommendation = "AERATE_DRYING"
        reason = f"Drying opportunity. Ambient EMC ({target_emc}%) is below grain moisture ({grain_moisture_pct}%)."
    else:
        recommendation = "HOLD_EQUILIBRIUM"
        reason = "Grain and ambient air are in near-equilibrium. Keep fans off to conserve power."
        
    return {
        "calculated_emc_pct": target_emc,
        "temp_differential_c": round(temp_diff, 1),
        "aeration_recommendation": recommendation,
        "agronomic_reason": reason,
        "is_safe_to_aerate": recommendation in ["AERATE_COOLING", "AERATE_DRYING"]
    }


def evaluate_condensation_risk(
    grain_temp_c: float,
    grain_moisture_pct: float,
    ambient_temp_c: float
) -> Tuple[int, str]:
    """
    Evaluates thermal shock condensation risk on steel bin roofs.
    When grain is warm and outside air freezes, warm rising air condenses on the cold steel roof,
    dripping water directly back onto the grain surface causing crusting and mycotoxin mold.
    
    Returns:
        (risk_level: 0=Safe, 1=Moderate, 2=Severe, description: str)
    """
    thermal_gradient = grain_temp_c - ambient_temp_c
    
    if thermal_gradient > 15.0 and grain_moisture_pct > 14.5:
        return 2, "CRITICAL: Severe roof condensation danger. Warm grain mass driving moisture into freezing headspace."
    elif thermal_gradient > 10.0 and grain_moisture_pct > 13.5:
        return 1, "MODERATE: Condensation risk detected. Schedule evening aeration to equalize headspace temperature."
    else:
        return 0, "SAFE: Headspace temperature gradient within safe non-condensing margins."
