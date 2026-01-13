from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime
import logging

from src.core.propagator import OrbitPropagator
from src.core.fusion import DataFusionEngine
from src.ml.anomaly_detector import AnomalyDetector

from src.api.routes_ssa import router as ssa_router, init_routes as init_ssa_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KoshaTrack SSA API",
    description="Sovereign Space Situational Awareness Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

propagator = OrbitPropagator()
fusion_engine = DataFusionEngine()
anomaly_detector = AnomalyDetector()

# SSA brain wiring
init_ssa_routes(fusion_engine, anomaly_detector)
app.include_router(ssa_router, prefix="/ssa", tags=["SSA Brain"])


class TLELoad(BaseModel):
    name: str
    line1: str
    line2: str


class PropagateRequest(BaseModel):
    sat_name: str
    time: Optional[datetime] = None


class CollisionCheck(BaseModel):
    sat1: str
    sat2: str
    time_window_days: int = 7


@app.get("/")
async def root():
    return {
        "name": "KoshaTrack SSA API",
        "version": "0.1.0",
        "status": "operational",
        "satellites_loaded": len(propagator.satellites),
    }


@app.post("/tle/load")
async def load_tle(tle: TLELoad):
    success = propagator.load_tle(tle.name, tle.line1, tle.line2)
    if success:
        return {"status": "success", "satellite": tle.name}
    raise HTTPException(status_code=400, detail="Failed to load TLE")


@app.post("/propagate")
async def propagate(req: PropagateRequest):
    time = req.time or datetime.utcnow()
    try:
        return propagator.propagate(req.sat_name, time)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/collision/check")
async def check_collision(req: CollisionCheck):
    try:
        return propagator.calculate_collision_probability(req.sat1, req.sat2, req.time_window_days)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/satellites")
async def list_satellites():
    return {"count": len(propagator.satellites), "satellites": list(propagator.satellites.keys())}


@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            updates = []
            for sat_name in list(propagator.satellites.keys())[:10]:
                try:
                    state = propagator.propagate(sat_name, datetime.utcnow())
                    updates.append(state)
                except Exception:
                    continue

            await websocket.send_json({"timestamp": datetime.utcnow().isoformat(), "satellites": updates})
            await asyncio.sleep(5)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
