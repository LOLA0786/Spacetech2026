"""
KoshaTrack SSA Engine - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import from ssa_engine (if it exists)
try:
    from ssa_engine.data.spacetrack_client import SpaceTrackClient
    SPACETRACK_AVAILABLE = True
except ImportError:
    print("⚠️  SpaceTrack client not available. Running in limited mode.")
    SPACETRACK_AVAILABLE = False

# Create FastAPI app
app = FastAPI(
    title="KoshaTrack SSA Engine",
    description="Tier-Zero Sovereign Space Situational Awareness Platform",
    version="0.1.0-alpha",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "name": "KoshaTrack SSA Engine",
        "version": "0.1.0-alpha",
        "status": "operational",
        "capabilities": {
            "hpop_propagation": True,
            "space_weather": True,
            "spacetrack_integration": SPACETRACK_AVAILABLE,
            "mht_tracking": False,  # Not yet implemented
            "hypersonic_detection": False,  # Not yet implemented
            "cislunar_tracking": False  # Not yet implemented
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# System info
@app.get("/api/v1/system/info")
def get_system_info():
    return {
        "system": "KoshaTrack SSA Engine",
        "description": "Sovereign Space Situational Awareness Platform",
        "features": [
            "High-Precision Orbit Propagation (HPOP)",
            "J2 Perturbation Modeling",
            "Solar Weather Integration",
            "Multi-Hypothesis Tracking (Planned)",
            "Hypersonic Threat Detection (Planned)",
            "Cislunar Awareness (Planned)"
        ],
        "dual_use": {
            "civil": ["Collision avoidance", "Insurance risk", "Launch planning"],
            "defense": ["Missile warning", "Contested domain awareness", "ASAT detection"]
        }
    }

# Placeholder for conjunction analysis
@app.get("/api/v1/conjunctions")
def get_conjunctions():
    """
    Get conjunction analysis results
    TODO: Implement actual conjunction detection
    """
    return {
        "message": "Conjunction analysis endpoint",
        "status": "not_implemented",
        "note": "Connect HPOP engine and implement screening logic"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     KoshaTrack SSA Engine - Tier-Zero Space Defense     ║
    ║                                                          ║
    ║  Status: Development Mode                               ║
    ║  Access: http://localhost:8000                          ║
    ║  Docs:   http://localhost:8000/docs                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
