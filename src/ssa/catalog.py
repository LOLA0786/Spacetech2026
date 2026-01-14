import requests
from typing import List, Dict
from datetime import datetime, timedelta

# Simple cache (5 min) to avoid hammering Celestrak
_catalog_cache: List[Dict] = []
_cache_time: datetime = datetime.min

CELESTRAK_ACTIVE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"

def _fetch_raw_tle() -> str:
    response = requests.get(CELESTRAK_ACTIVE_URL, timeout=15)
    response.raise_for_status()
    return response.text

def get_active_catalog(limit: int = 150) -> List[Dict[str, str]]:
    """
    Returns list of dicts: {"name": str, "line1": str, "line2": str}
    Limited to 150 for fast demo screening (full active ~5000+, use SpaceTrack for sovereign scale)
    """
    global _catalog_cache, _cache_time
    
    now = datetime.utcnow()
    if _catalog_cache and (now - _cache_time) < timedelta(minutes=5):
        return _catalog_cache[:limit]
    
    try:
        raw = _fetch_raw_tle()
        lines = raw.strip().splitlines()
        
        catalog = []
        i = 0
        while i < len(lines) - 2:
            name = lines[i].strip() or f"OBJECT {len(catalog)+1}"
            line1 = lines[i+1].strip()
            line2 = lines[i+2].strip()
            if line1.startswith("1 ") and line2.startswith("2 "):
                catalog.append({"name": name, "line1": line1, "line2": line2})
            i += 3
        
        _catalog_cache = catalog
        _cache_time = now
        print(f"Loaded {len(catalog)} active satellites from Celestrak (cached 5 min)")
        return catalog[:limit]
    except Exception as e:
        raise RuntimeError(f"Failed to load catalog: {e}")
