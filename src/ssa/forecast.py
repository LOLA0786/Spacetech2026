import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict

from .propagator import propagate_tle
from .catalog import get_active_catalog

def forecast_indian_threats(hours: int = 24, steps: int = 24) -> Dict:
    """
    Forecast risks to Indian sovereign assets over next N hours
    steps = hourly checks for smooth coverage
    """
    catalog = get_active_catalog(limit=300)
    indian_sats = [sat for sat in catalog if sat["is_indian"]]
    other_sats = [sat for sat in catalog if not sat["is_indian"]]
    
    if not indian_sats:
        return {"status": "No Indian assets in current snapshot", "forecast": []}
    
    forecast_risks = []
    base_time = datetime.utcnow()
    
    for step in range(steps + 1):
        dt = base_time + timedelta(hours=step * hours / steps)
        
        # Propagate all
        positions = {}
        for sat in catalog:
            try:
                result = propagate_tle(sat["line1"], sat["line2"], dt)
                positions[sat["name"]] = np.array(result["position_eci_km"])
            except ValueError:
                continue
        
        # Check Indian vs all others
        for ind_sat in indian_sats:
            if ind_sat["name"] not in positions:
                continue
            ind_pos = positions[ind_sat["name"]]
            
            for other in other_sats:
                if other["name"] not in positions:
                    continue
                dist_km = np.linalg.norm(ind_pos - positions[other["name"]])
                
                if dist_km < 200:  # Forecast wider net
                    risk_level = "CRITICAL FORECAST" if dist_km < 10 else "ELEVATED FORECAST" if dist_km < 50 else "MONITOR FORECAST"
                    
                    forecast_risks.append({
                        "indian_asset": ind_sat["name"],
                        "threat_object": other["name"],
                        "predicted_tca_utc": dt.isoformat() + "Z",
                        "predicted_distance_km": round(dist_km, 3),
                        "risk_level": risk_level,
                        "defense_alert": "FUTURE THREAT TO INDIAN SOVEREIGN ASSET - ADVANCE WARNING"
                    })
    
    # Sort by closest predicted distance
    forecast_risks.sort(key=lambda x: x["predicted_distance_km"])
    
    return {
        "forecast_period_hours": hours,
        "assessment_time_utc": datetime.utcnow().isoformat() + "Z",
        "steps": steps,
        "indian_assets_monitored": [s["name"] for s in indian_sats],
        "total_predicted_risks": len(forecast_risks),
        "top_forecast_risks": forecast_risks[:20],
        "mission_note": "KoshaTrack Predictive Tier-Zero - Early Warning for Bharatiya Antriksh Security 🇮🇳"
    }
