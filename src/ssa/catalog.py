# ... (keep existing imports and INDIAN_KEYWORDS)

def get_active_catalog(limit: int = 300) -> List[Dict]:
    if SPACETRACK_AVAILABLE:
        try:
            from ..ssa_engine.data.spacetrack_client import fetch_full_catalog
            return fetch_full_catalog(limit=limit * 10)  # More with SpaceTrack
        except:
            print("SpaceTrack fetch failed - fallback to Celestrak")
    
    # Existing Celestrak code...
    # (keep the previous Celestrak fetch logic as fallback)
