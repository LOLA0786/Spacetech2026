import os
from dotenv import load_dotenv

load_dotenv()

try:
    from spacetrack import SpaceTrackClient as BaseClient
    username = os.getenv('SPACETRACK_USERNAME')
    password = os.getenv('SPACETRACK_PASSWORD')
    
    st_client = BaseClient(identity=username, password=password) if username and password else None
    
    if st_client:
        print("SpaceTrack authenticated - Tier-Zero full catalog enabled 🇮🇳")
    else:
        print("SpaceTrack credentials missing - fallback to public Celestrak")
except ImportError:
    st_client = None
    print("spacetrack package not available")

def is_available() -> bool:
    return st_client is not None

# Example: fetch latest TLE for NORAD ID (extend for full catalog, boxscore, etc.)
def fetch_latest_tle(norad_id: int) -> tuple[str, str]:
    if not st_client:
        raise RuntimeError("SpaceTrack not authenticated")
    data = st_client.tle_latest(norad_cat_id=[norad_id], ordinal=1, format='tle')
    lines = data.splitlines()
    if len(lines) >= 2:
        return lines[0].strip(), lines[1].strip()
    raise ValueError(f"No TLE for NORAD {norad_id}")
