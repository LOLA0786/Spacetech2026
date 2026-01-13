"""
Space Insurance Risk Assessment API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np

router = APIRouter(prefix="/api/v1/insurance", tags=["Insurance"])

class RiskAssessmentRequest(BaseModel):
    satellite_id: str
    norad_id: int
    mission_duration_years: float
    orbital_regime: str  # LEO, MEO, GEO
    asset_value_usd: float

class RiskAssessmentResponse(BaseModel):
    satellite_id: str
    annual_collision_probability: float
    mission_lifetime_risk: float
    expected_loss_usd: float
    premium_multiplier: float
    risk_factors: dict
    recommendations: List[str]

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def calculate_insurance_risk(request: RiskAssessmentRequest):
    """
    Calculate actuarial risk for space insurance
    """
    # Get conjunction history for this satellite
    from src.core.conjunction_analyzer import ConjunctionAnalyzer
    analyzer = ConjunctionAnalyzer()
    
    # Historical conjunction data
    conjunctions = analyzer.get_conjunction_history(
        request.norad_id, 
        lookback_days=365
    )
    
    # Calculate base collision probability
    if request.orbital_regime == "LEO":
        base_prob = 0.0001  # 0.01% per year
        density_factor = len(conjunctions) / 100  # Adjust for traffic
    elif request.orbital_regime == "MEO":
        base_prob = 0.00005
        density_factor = len(conjunctions) / 50
    else:  # GEO
        base_prob = 0.00001
        density_factor = len(conjunctions) / 20
    
    annual_prob = base_prob * (1 + density_factor)
    
    # Mission lifetime risk (compound probability)
    lifetime_risk = 1 - (1 - annual_prob) ** request.mission_duration_years
    
    # Expected loss
    expected_loss = lifetime_risk * request.asset_value_usd
    
    # Premium multiplier (industry standard: 1-3%)
    premium_multiplier = 0.01 + (lifetime_risk * 2)
    
    # Risk factors breakdown
    risk_factors = {
        "orbital_density": density_factor,
        "debris_exposure": len([c for c in conjunctions if c['type'] == 'debris']) / len(conjunctions) if conjunctions else 0,
        "maneuverable": True,  # Assume has propulsion
        "solar_cycle_phase": "approaching_maximum",  # From space weather
    }
    
    # Recommendations
    recommendations = []
    if lifetime_risk > 0.05:
        recommendations.append("Consider collision avoidance service subscription")
    if len(conjunctions) > 50:
        recommendations.append("High-traffic orbit - recommend higher coverage")
    if request.orbital_regime == "LEO":
        recommendations.append("LEO drag uncertainty - weather monitoring recommended")
    
    return RiskAssessmentResponse(
        satellite_id=request.satellite_id,
        annual_collision_probability=annual_prob,
        mission_lifetime_risk=lifetime_risk,
        expected_loss_usd=expected_loss,
        premium_multiplier=premium_multiplier,
        risk_factors=risk_factors,
        recommendations=recommendations
    )

@router.get("/market-trends")
async def get_insurance_market_trends():
    """
    Global space insurance market analytics
    """
    return {
        "total_market_size_usd": 500_000_000,
        "growth_rate": 0.08,
        "average_premium_rate": 0.02,
        "claims_ratio": 0.15,
        "top_risks": [
            "LEO mega-constellation congestion",
            "Solar cycle maximum approaching",
            "Increasing ASAT testing"
        ]
    }
