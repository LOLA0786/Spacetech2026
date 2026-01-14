"""
KoshaTrack SSA Engine

Tier-Zero Sovereign Space Situational Awareness Platform
Developed for India's Ministry of Defence (iDEX ADITI)

Features:
- High-Precision Orbit Propagation (HPOP)
- Physics-informed Zero-Trust Verification
- Red-Black Separation Architecture
- Sovereign Kubernetes Deployment

License: PolyForm Noncommercial (Free for GoI national security use)
"""

__version__ = "0.1.0-alpha"
__author__ = "LOLA0786"
__description__ = "Sovereign Space Defense SSA Engine"

# Safe public API - explicitly expose what grows
__all__ = [
    "app",                  # FastAPI app (once imported in main)
]

# Optional: auto-import common modules when package is imported
try:
    from .main import app
except ImportError:
    app = None  # Graceful if running outside package

try:
    from .ssa.propagator import propagate_tle, get_iss_position_now
except ImportError:
    propagate_tle = None
    get_iss_position_now = None

# Package-level logger setup (add later when logging module exists)
# import logging
# logging.getLogger(__name__).addHandler(logging.NullHandler())
