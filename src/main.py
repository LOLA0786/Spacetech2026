"""
KoshaTrack SSA Engine - Main FastAPI Application
Tier-Zero Sovereign Space Situational Awareness Platform
"""

import sys
from pathlib import Path
from datetime import datetime

# Global tracking for live status
last_propagation_time: str | None = None

# Global tracking for demo
last_propagation_time: str | None = None

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

# Clean FastAPI initialization

try:
        from .ssa_engine.data.spacetrack_client import is_available
        SPACETRACK_AVAILABLE = is_available()
except Exception as e:
        print(f"Warning: SpaceTrack integration disabled: {e}")
        SPACETRACK_AVAILABLE = False






# FastAPI app initialization

# SpaceTrack placeholder (keep for future)

    title="KoshaTrack SSA Engine",

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None
    description="Tier-Zero Sovereign Space Situational Awareness Platform",

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None
    version=__version__,  # Pulled from package __init__.py

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None
    docs_url="/docs",

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None
    redoc_url="/redoc"

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None
)

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None

# CORS - tighten later for zero-trust
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to sovereign domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
        return {"success": True, "iss_zarya": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid TLE/physics check: {str(e)}")

@app.post("/api/v1/propagate")
def custom_propagate(tle: TLEInput):
    if not PROPAGATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Propagation engine not ready")
    try:
        result = propagate_tle(tle.line1, tle.line2)
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
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
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
    app.state.last_propagation_time = datetime.utcnow().isoformat() + "Z"
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

# At top with other imports
from datetime import datetime

# Global tracking for live status
last_propagation_time: str | None = None

# Global tracking for demo
last_propagation_time: str | None = None

# Add global for demo tracking (simple)
last_propagation_time = None

# In both demo_iss_position and custom_propagate after success:

# Update read_root() to include:
    "last_successful_propagation": last_propagation_time or "None yet",
    "demo_note": "Custom TLE propagation fully operational - physics verified"
        "predictive_forecast": True,

from fastapi import Query
from .ssa.forecast import forecast_indian_threats

@app.get("/api/v1/conjunctions/forecast", tags=["defense"])
def forecast_conjunctions(hours: int = Query(24, description="Forecast horizon in hours"), steps: int = Query(24, description="Prediction steps")):
    """Predictive Conjunction Forecasting - Focused on Indian Sovereign Asset Protection"""
    try:
        result = forecast_indian_threats(hours=hours, steps=steps)
        return {
            "system": "KoshaTrack SSA Engine - Predictive Defense Mode",
            "directive": "iDEX ADITI Advance Warning System",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")
        "demo_note": "Custom TLE propagation + Indian asset screening fully operational",
        "predictive_forecast": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

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
app = FastAPI(
    title="KoshaTrack SSA Engine",
    description="Tier-Zero Sovereign Space Situational Awareness Platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Live status tracking (FastAPI best practice)
app.state.last_propagation_time = None

from fastapi.responses import StreamingResponse
from io import BytesIO

from .ssa.visualize import generate_indian_orbits_plot

@app.get("/api/v1/visualize/indian_orbits", tags=["defense", "visualization"])
def visualize_indian_orbits():
    """Live 3D orbit visualization - Indian assets highlighted in lime green on black space background"""
    image_bytes = generate_indian_orbits_plot()
    return StreamingResponse(BytesIO(image_bytes), media_type="image/png")

from fastapi.responses import StreamingResponse
from io import BytesIO

from .ssa.visualize import generate_indian_orbits_plot

@app.get("/api/v1/visualize/indian_orbits", tags=["defense", "visualization"])
def visualize_indian_orbits():
    """Live black-space 3D orbit PNG - Indian sovereign assets in lime green (iDEX gold)"""
    image_bytes = generate_indian_orbits_plot()
    return StreamingResponse(BytesIO(image_bytes), media_type="image/png")

from fastapi.responses import StreamingResponse

from .ssa.report import generate_mod_briefing_pdf

@app.get("/api/v1/report/mod_briefing.pdf", tags=["defense"])
def mod_briefing_pdf():
    """PDF briefing report for Ministry of Defence - risks + orbit visualization"""
    pdf_bytes = generate_mod_briefing_pdf()
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=koshatrack_mod_briefing.pdf"})
