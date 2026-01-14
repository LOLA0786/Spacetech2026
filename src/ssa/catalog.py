import requests
from typing import List, Dict
from datetime import datetime, timedelta

# Cache
_catalog_cache: List[Dict] = []
_cache_time: datetime = datetime.min

CELESTRAK_ACTIVE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"

# Comprehensive Indian satellite name patterns (covers ISRO/DRDO assets)
INDIAN_KEYWORDS = [
    "GSAT", "INSAT", "CARTOSAT", "RISAT", "IRNSS", "NAVIC", "NVS-", 
    "EOS-", "CMS-", "OCEANSAT", "RESOURCESAT", "SCATSAT", "HY SIS",
    "MICROSAT", "EMISAT", "GISAT", "ADITYA", "ANVESHA", "SPADEX",
    "ISRO", "INDIA", "BHASKARA", "ARYABHATA"
]

def _fetch_raw_tle() -> str:
    response = requests.get(CELESTRAK_ACTIVE_URL, timeout=20)
    response.raise_for_status()
    return response.text

def get_active_catalog(limit: int = 300) -> List[Dict[str, str]]:
    """
    Returns enriched catalog with Indian flag
    Limit 300 for fast defense screening (full active ~5000+, SpaceTrack for sovereign)
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
                is_indian = any(kw in name.upper() for kw in INDIAN_KEYWORDS)
                is_debris = "DEB" in name.upper() or "ROCKET" in name.upper() or "DEBRIS" in name.upper()
                
                catalog.append({
                    "name": name,
                    "line1": line1,
                    "line2": line2,
                    "is_indian": is_indian,
                    "is_debris": is_debris
                })
            i += 3
        
        _catalog_cache = catalog
        _cache_time = now
        indian_count = sum(1 for s in catalog if s["is_indian"])
        print(f"Loaded {len(catalog)} active satellites | {indian_count} Indian sovereign assets detected (cached 5 min)")
        return catalog[:limit]
    except Exception as e:
        raise RuntimeError(f"Failed to load catalog: {e}")
