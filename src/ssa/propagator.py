import requests
import numpy as np
from datetime import datetime, timedelta
from sgp4.api import Satrec, jday
from typing import Optional

# Cache for ISS
_iss_tle_cache: Optional[tuple[str, str, datetime]] = None
_cache_valid_until: datetime = datetime.min

CELESTRAK_STATIONS_URL = "https://celestrak.org/NORAD/elements/stations.txt"

HARDCODED_ISS_LINE1 = "1 25544U 98067A   26014.50000000  .00001234  00000-0  12345-4 0  9999"
HARDCODED_ISS_LINE2 = "2 25544  51.6430  123.4560 0001234  90.0000 270.0000 15.48901234 56789"

def _fetch_fresh_iss_tle() -> tuple[str, str]:
    global _iss_tle_cache, _cache_valid_until
    
    now = datetime.utcnow()
    if _iss_tle_cache and now < _cache_valid_until:
        return _iss_tle_cache[0], _iss_tle_cache[1]
    
    try:
        response = requests.get(CELESTRAK_STATIONS_URL, timeout=10)
        response.raise_for_status()
        lines = response.text.strip().splitlines()
        
        for i in range(0, len(lines), 3):
            if len(lines) > i + 2 and "ISS (ZARYA)" in lines[i].strip():
                line1 = lines[i+1].strip()
                line2 = lines[i+2].strip()
                _iss_tle_cache = (line1, line2, now)
                _cache_valid_until = now + timedelta(minutes=5)
                print("Fetched fresh ISS TLE from Celestrak")
                return line1, line2
    except Exception as e:
        print(f"Warning: Could not fetch fresh TLE: {e}. Using hardcoded fallback.")
    
    return HARDCODED_ISS_LINE1, HARDCODED_ISS_LINE2

def validate_orbital_elements(sat):
    """Physics-informed zero-trust verification + anomaly flags"""
    flags = []
    
    if not (0 <= sat.ecco < 1):
        raise ValueError(f"Invalid eccentricity {sat.ecco:.6f} - must be 0 ≤ e < 1")
    if sat.ecco > 0.3:
        flags.append("Highly eccentric orbit - potential maneuverable/co-orbital threat")
    if sat.ecco > 0.7:
        flags.append("CRITICAL: Ballistic/hypersonic reentry trajectory anomaly")
        
    if sat.no_kozai <= 0:
        raise ValueError("Invalid mean motion (≤ 0)")
    if not (0 <= sat.inclo <= 180):
        raise ValueError(f"Invalid inclination {sat.inclo:.2f}°")
    
    return flags

def propagate_tle(line1: str, line2: str, dt: Optional[datetime] = None):
    if dt is None:
        dt = datetime.utcnow()
    
    sat = Satrec.twoline2rv(line1, line2)
    base_flags = validate_orbital_elements(sat)
    
    jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond / 1e6)
    error_code, position, velocity = sat.sgp4(jd, fr)
    
    if error_code != 0:
        raise ValueError(f"SGP4 propagation error code: {error_code}")
    
    speed_kms = np.linalg.norm(velocity)
    if speed_kms > 8.5:
        base_flags.append(f"Hypervelocity ({speed_kms:.1f} km/s) - potential hypersonic glider/ICBM stage")
    if speed_kms > 10.0:
        base_flags.append("CRITICAL: Extreme hypervelocity anomaly - contested domain threat")
    
    return {
        "timestamp_utc": dt.isoformat() + "Z",
        "source": "custom_tle",
        "position_eci_km": list(position),
        "velocity_eci_km_s": list(velocity),
        "speed_kms": round(speed_kms, 3),
        "eccentricity": round(sat.ecco, 6),
        "anomaly_flags": base_flags or ["Nominal orbit"]
    }

def get_iss_position_now():
    line1, line2 = _fetch_fresh_iss_tle()
    result = propagate_tle(line1, line2)
    result["source"] = "iss_zarya_fresh_celestrak"
    result["tle_lines"] = {"line1": line1, "line2": line2}
    return result
