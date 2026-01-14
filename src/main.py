"""
KoshaTrack SSA Engine - Main FastAPI Application
Tier-Zero Sovereign Space Situational Awareness Platform
"""

import sys
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env early
load_dotenv()

# Make project root importable (optional safety for scripts)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Package metadata
from . import __version__

# Propagation availability (relative import - package style)
try:
    from .ssa.propagator import propagate_tle, get_iss_position_now
    PROPAGATION_AVAILABLE = True
except Exception as e:
    print(f"Warning: Propagation module not available: {e}")
    PROPAGATION_AVAILABLE = False

# SpaceTrack integration (Tier-Zero sovereign full catalog)
try:
    from .ssa_engine.data.spacetrack_client import is_available
    SPACETRACK_AVAILABLE = is_available()
except Exception as e:
    print(f"Warning: SpaceTrack integration disabled: {e}")
    SPACETRACK_AVAILABLE = False


# SpaceTrack integration (Tier-Zero sovereign full catalog)
try:
except Exception as e:
    print(f"Warning: SpaceTrack integration disabled: {e}")
    SPACETRACK_AVAILABLE = False


# SpaceTrack placeholder (keep for future)

app = FastAPI(
    title="KoshaTrack SSA Engine",
    description="Tier-Zero Sovereign Space Situational Awareness Platform",
    version=__version__,  # Pulled from package __init__.py
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - tighten later for zero-trust
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to sovereign domains
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
        "capabilities": {
            "hpop_propagation": PROPAGATION_AVAILABLE,
            "basic_sgp4_propagation": PROPAGATION_AVAILABLE,
            "physics_verification": PROPAGATION_AVAILABLE,
            "space_weather": True,
            "spacetrack_integration": SPACETRACK_AVAILABLE,  # Full 30k+ object catalog with MoD credentials,
            "mht_tracking": False,
            "hypersonic_detection": False,
            "cislunar_tracking": False
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/api/v1/system/info")
def get_system_info():
    return {
        "system": "KoshaTrack SSA Engine",
        "version": __version__,
        "description": "Sovereign Space Situational Awareness Platform",
        "features": [
            "High-Precision Orbit Propagation (HPOP - in progress)",
            "SGP4 Basic Propagation (active)",
            "Physics-informed Zero-Trust Verification (active)",
            "J2 Perturbation Modeling (planned)",
            "Solar Weather Integration (planned)",
            "Multi-Hypothesis Tracking (planned)",
            "Hypersonic Threat Detection (planned)",
            "Cislunar Awareness (planned)"
        ],
        "dual_use": {
            "civil": ["Collision avoidance", "Insurance risk", "Launch planning"],
            "defense": ["Missile warning", "Contested domain awareness", "ASAT detection"]
        }
    }

@app.get("/api/v1/conjunctions")
def get_conjunctions():
    return {
        "message": "Conjunction analysis endpoint",
        "status": "in_development",
        "note": "HPOP + screening coming soon"
    }

# === Propagation Endpoints ===
class TLEInput(BaseModel):
    line1: str
    line2: str

@app.get("/api/v1/demo/iss_position")
def demo_iss_position():
    if not PROPAGATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Propagation engine not ready")
    try:
        result = get_iss_position_now()
        return {"success": True, "iss_zarya": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid TLE/physics check: {str(e)}")

@app.post("/api/v1/propagate")
def custom_propagate(tle: TLEInput):
    if not PROPAGATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Propagation engine not ready")
    try:
        result = propagate_tle(tle.line1, tle.line2)
        return {"success": True, "propagation": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Propagation failed: {str(e)}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║     KoshaTrack SSA Engine v{__version__} - Tier-Zero Space Defense     ║
    ║                                                          ║
    ║  Status: Development Mode                               ║
    ║  Access: http://localhost:8000                          ║
    ║  Docs:   http://localhost:8000/docs                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.main:app",  # Explicit module path for direct run
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

@app.get("/api/v1/demo/iss_position")
def demo_iss_position():
    if not PROPAGATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Propagation engine not ready")
    try:
        result = get_iss_position_now()
        return {
            "success": True,
            "data": result,
            "note": "TLE fetched live from Celestrak (cached 5 min) with physics verification"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid TLE/physics check: {str(e)}")

from .ssa.screening import screen_conjunctions

@app.get("/api/v1/conjunctions/screen")
def conjunction_screen():
    """Defense-grade conjunction screening endpoint"""
    try:
        result = screen_conjunctions()
        return {
            "system": "KoshaTrack SSA Engine - Tier-Zero Sovereign SSA",
            "mission": "Early warning for India's space domain security (iDEX ADITI)",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening failed: {str(e)}")

@app.get("/api/v1/conjunctions/screen", tags=["defense"])
def conjunction_screen():
    """Tier-Zero Defense Conjunction Screening - Sovereign Asset Protection Focus"""
    try:
        result = screen_conjunctions()
        return {
            "system": "KoshaTrack SSA Engine v0.1.0-alpha",
            "mission_directive": "iDEX ADITI - Tier-Zero Space Domain Awareness for India's Ministry of Defence",
            "mumbai_to_orbit": "Operational from Maharashtra 🇮🇳",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Defense screening failed: {str(e)}")
