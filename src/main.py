"""
KoshaTrack SSA Engine - Main FastAPI Application
Tier-Zero Sovereign Space Situational Awareness Platform
"""

import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from . import __version__

try:
    from .ssa.propagator import propagate_tle, get_iss_position_now
    PROPAGATION_AVAILABLE = True
except Exception as e:
    print(f"Warning: Propagation module not available: {e}")
    PROPAGATION_AVAILABLE = False

try:
    from .ssa_engine.data.spacetrack_client import is_available
    SPACETRACK_AVAILABLE = is_available()
except Exception as e:
    print(f"Warning: SpaceTrack integration disabled: {e}")
    SPACETRACK_AVAILABLE = False

app = FastAPI(
    title="KoshaTrack SSA Engine",
    description="Tier-Zero Sovereign Space Situational Awareness Platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "name": "KoshaTrack SSA Engine",
        "version": __version__,
        "status": "operational",
        "last_successful_propagation": app.state.last_propagation_time or "None yet",
        "capabilities": {
            "basic_sgp4_propagation": PROPAGATION_AVAILABLE,
            "physics_verification": PROPAGATION_AVAILABLE,
            "indian_asset_protection": True,
            "predictive_forecast": True,
            "hypersonic_detection": True,
            "spacetrack_ready": SPACETRACK_AVAILABLE
        },
        "live_note": "Tier-Zero operational from Mumbai 🇮🇳 - Protecting Bharatiya Antriksh Domain",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# Add your other endpoints here (health, iss, propagate, screening, forecast, etc.) from previous builds

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
