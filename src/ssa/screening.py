import numpy as np
from datetime import datetime
from typing import List, Dict

from .propagator import propagate_tle
from .catalog import get_active_catalog

def get_current_positions(catalog: List[Dict]) -> Dict[str, np.ndarray]:
    positions = {}
    dt = datetime.utcnow()
    for sat in catalog:
        try:
            result = propagate_tle(sat["line1"], sat["line2"], dt)
            positions[sat["name"]] = np.array(result["position_eci_km"])
        except ValueError:
            continue  # Skip invalid/physics-rejected
    return positions

def assess_conjunction_risks(positions: Dict[str, np.ndarray]) -> List[Dict]:
    names = list(positions.keys())
    risks = []
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            dist_km = np.linalg.norm(positions[names[i]] - positions[names[j]])
            
            if dist_km < 100:  # Only report interesting approaches
                risk_level = "MONITOR"
                if dist_km < 10:
                    risk_level = "ELEVATED"
                if dist_km < 1:
                    risk_level = "CRITICAL - IMMEDIATE ASSESSMENT REQUIRED"
                
                risks.append({
                    "primary": names[i],
                    "secondary": names[j],
                    "distance_km": round(dist_km, 3),
                    "risk_level": risk_level,
                    "domain_implication": "Potential collision risk in contested LEO domain"
                })
    
    risks.sort(key=lambda x: x["distance_km"])
    return risks[:20]  # Top 20 closest for clean output

def screen_conjunctions() -> Dict:
    catalog = get_active_catalog(limit=150)
    positions = get_current_positions(catalog)
    
    risks = assess_conjunction_risks(positions)
    
    return {
        "assessment_timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "satellites_screened": len(positions),
        "catalog_source": "Celestrak Active (public) - limited for demo",
        "sovereign_note": "For Tier-Zero defense: integrate SpaceTrack credentials for full 30k+ object catalog (incl. debris, classified threats)",
        "potential_risks": risks,
        "status": f"{len(risks)} close approaches detected (<100km)" if risks else "No immediate high-risk conjunctions in current snapshot"
    }
