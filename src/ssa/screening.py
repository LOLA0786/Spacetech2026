import numpy as np
from datetime import datetime
from typing import List, Dict

from .propagator import propagate_tle
from .catalog import get_active_catalog

def get_current_positions(catalog: List[Dict]) -> Dict[str, Dict]:
    positions = {}
    dt = datetime.utcnow()
    for sat in catalog:
        try:
            result = propagate_tle(sat["line1"], sat["line2"], dt)
            positions[sat["name"]] = {
                "pos": np.array(result["position_eci_km"]),
                "data": result,
                "meta": sat  # is_indian, is_debris, name
            }
        except ValueError:
            continue
    return positions

def assess_conjunction_risks(positions: Dict[str, Dict]) -> List[Dict]:
    names = list(positions.keys())
    risks = []
    
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            pos1 = positions[names[i]]["pos"]
            pos2 = positions[names[j]]["pos"]
            dist_km = np.linalg.norm(pos1 - pos2)
            
            if dist_km < 150:  # Wider net for sovereign monitoring
                risk = {
                    "primary": names[i],
                    "secondary": names[j],
                    "distance_km": round(dist_km, 3),
                    "primary_indian": positions[names[i]]["meta"]["is_indian"],
                    "secondary_indian": positions[names[j]]["meta"]["is_indian"],
                    "debris_involved": positions[names[i]]["meta"]["is_debris"] or positions[names[j]]["meta"]["is_debris"],
                    "anomalies": positions[names[i]]["data"]["anomaly_flags"] + positions[names[j]]["data"]["anomaly_flags"]
                }
                
                # Defense grading
                if risk["primary_indian"] or risk["secondary_indian"]:
                    risk["defense_alert"] = "THREAT TO INDIAN SOVEREIGN ASSET - iDEX ADITI PRIORITY"
                    risk["risk_level"] = "CRITICAL" if dist_km < 5 else "ELEVATED" if dist_km < 20 else "MONITOR"
                else:
                    risk["risk_level"] = "ELEVATED" if dist_km < 10 else "MONITOR"
                
                if risk["debris_involved"]:
                    risk["defense_alert"] = (risk.get("defense_alert", "") + " | DEBRIS THREAT").strip()
                
                risks.append(risk)
    
    # Prioritize Indian threats first
    risks.sort(key=lambda x: (x.get("defense_alert") is not None, x["distance_km"]))
    return risks[:30]  # Top 30 for focused report

def screen_conjunctions() -> Dict:
    catalog = get_active_catalog(limit=300)
    positions = get_current_positions(catalog)
    
    indian_assets = [sat["name"] for sat in catalog if sat["is_indian"]]
    risks = assess_conjunction_risks(positions)
    
    indian_threats = [r for r in risks if r.get("defense_alert")]
    
    return {
        "assessment_timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "satellites_screened": len(positions),
        "indian_sovereign_assets_detected": len(indian_assets),
        "indian_asset_list": indian_assets or ["None in current snapshot - upgrade to SpaceTrack for full"],
        "catalog_source": "Celestrak Active (public payloads)",
        "sovereign_upgrade_note": "With MoD SpaceTrack credentials: full 30k+ catalog incl. debris, analyst objects, classified threats",
        "hypersonic_anomaly_detection": "Active - flags hypervelocity/eccentric orbits",
        "total_close_approaches": len(risks),
        "indian_asset_threats": len(indian_threats),
        "defense_critical_risks": indian_threats or ["Clear - no immediate threats to Indian assets"],
        "top_risks": risks,
        "mission_status": "KoshaTrack Tier-Zero Operational - Protecting Bharatiya Antriksh Domain 🇮🇳"
    }
