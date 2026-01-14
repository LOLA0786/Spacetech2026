import os
from dotenv import load_dotenv

load_dotenv()

try:
    from spacetrack import SpaceTrackClient as BaseClient
    username = os.getenv('SPACETRACK_USERNAME')
    password = os.getenv('SPACETRACK_PASSWORD')
    
    st = BaseClient(identity=username, password=password) if username and password else None
    
    if st:
        print("SpaceTrack authenticated - Full Tier-Zero catalog (30k+ incl. debris/classified) ENABLED 🇮🇳")
except ImportError:
    st = None
    print("spacetrack package missing")

def is_available() -> bool:
    return st is not None

def fetch_full_catalog(limit: int = 500) -> list:
    if not st:
        raise RuntimeError("SpaceTrack credentials missing - fallback to Celestrak")
    
    # Fetch latest TLE for active + debris (analyst objects for classified)
    data = st.tle_latest(iter_lines=True, object_type=['PAYLOAD', 'DEBRIS', 'ROCKET BODY'], ordinal=1)
    catalog = []
    name = "UNKNOWN"
    for line in data:
        if line.startswith('0 '):
            name = line[2:].strip()
        elif line.startswith('1 '):
            line1 = line.strip()
        elif line.startswith('2 '):
            line2 = line.strip()
            catalog.append({"name": name, "line1": line1, "line2": line2, "is_debris": "DEB" in name.upper() or "ROCKET" in name.upper()})
            if len(catalog) >= limit:
                break
    print(f"Fetched {len(catalog)} objects from SpaceTrack full catalog")
    return catalog
