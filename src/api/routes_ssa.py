from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from src.core.fusion import DataFusionEngine
from src.ml.anomaly_detector import AnomalyDetector

logger = logging.getLogger(__name__)
router = APIRouter()

fusion_engine: Optional[DataFusionEngine] = None
anomaly_detector: Optional[AnomalyDetector] = None


class RegisterSourceRequest(BaseModel):
    name: str
    reliability: float = Field(ge=0.0, le=1.0)
    latency_ms: int = Field(ge=0)


class IngestObservationRequest(BaseModel):
    source: str
    object_id: str
    position: Optional[Dict[str, float]] = None
    velocity: Optional[Dict[str, float]] = None
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)


class FuseRequest(BaseModel):
    time_window_hours: int = Field(default=1, ge=1, le=168)


class TrajectoryPoint(BaseModel):
    timestamp: datetime
    position: Dict[str, float]
    velocity: Dict[str, float]


class TrainAnomalyRequest(BaseModel):
    normal_trajectories: List[List[TrajectoryPoint]]


class DetectAnomalyRequest(BaseModel):
    trajectory: List[TrajectoryPoint]


# -----------------------
# Sovereign Local Ledger
# -----------------------
import json
import hashlib

LOCAL_LEDGER: List[Dict[str, Any]] = []


class RecordEventRequest(BaseModel):
    event_type: str
    object_id: str
    data: Dict[str, Any]
    signer: str = "kosha_local"


def _hash_event(event: Dict[str, Any]) -> str:
    event_json = json.dumps(event, sort_keys=True)
    return hashlib.sha256(event_json.encode("utf-8")).hexdigest()


def init_routes(fusion: DataFusionEngine, detector: AnomalyDetector):
    global fusion_engine, anomaly_detector
    fusion_engine = fusion
    anomaly_detector = detector
    logger.info("SSA brain routes initialized.")


@router.post("/fusion/source/register")
def register_source(req: RegisterSourceRequest):
    if fusion_engine is None:
        raise HTTPException(500, "Fusion engine not initialized")
    fusion_engine.register_source(req.name, req.reliability, req.latency_ms)
    return {"status": "ok", "source": req.name}


@router.post("/fusion/ingest")
def ingest_observation(req: IngestObservationRequest):
    if fusion_engine is None:
        raise HTTPException(500, "Fusion engine not initialized")

    obs = fusion_engine.ingest_observation(
        source=req.source,
        obj_id=req.object_id,
        data={
            "position": req.position,
            "velocity": req.velocity,
            "confidence": req.confidence,
        },
    )
    return {"status": "ok", "observation": obs}


@router.post("/fusion/fuse/{object_id}")
def fuse_object(object_id: str, req: FuseRequest):
    if fusion_engine is None:
        raise HTTPException(500, "Fusion engine not initialized")
    result = fusion_engine.fuse(object_id, time_window_hours=req.time_window_hours)
    return {"status": "ok", "result": result}


@router.get("/fusion/history/{object_id}")
def fusion_history(object_id: str):
    if fusion_engine is None:
        raise HTTPException(500, "Fusion engine not initialized")
    history = [h for h in fusion_engine.fusion_history if h.get("object_id") == object_id]
    return {"status": "ok", "object_id": object_id, "count": len(history), "history": history}


@router.post("/anomaly/train")
def anomaly_train(req: TrainAnomalyRequest):
    if anomaly_detector is None:
        raise HTTPException(500, "Anomaly detector not initialized")

    normal = []
    for traj in req.normal_trajectories:
        normal.append(
            [
                {"timestamp": p.timestamp, "position": p.position, "velocity": p.velocity}
                for p in traj
            ]
        )

    anomaly_detector.train(normal)
    return {"status": "ok", "trained": True}


@router.post("/anomaly/detect")
def anomaly_detect(req: DetectAnomalyRequest):
    if anomaly_detector is None:
        raise HTTPException(500, "Anomaly detector not initialized")

    traj = [{"timestamp": p.timestamp, "position": p.position, "velocity": p.velocity} for p in req.trajectory]
    result = anomaly_detector.detect(traj)
    return {"status": "ok", "result": result}


@router.post("/ledger/record")
def ledger_record(req: RecordEventRequest):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": req.event_type,
        "object_id": req.object_id,
        "data": req.data,
        "signer": req.signer,
    }
    h = _hash_event(event)
    LOCAL_LEDGER.append({"event": event, "hash": h})
    return {"status": "ok", "hash": h, "event": event}


@router.get("/ledger/verify/{event_hash}")
def ledger_verify(event_hash: str):
    for entry in LOCAL_LEDGER:
        if entry["hash"] == event_hash:
            computed = _hash_event(entry["event"])
            return {"status": "ok", "exists": True, "valid": computed == event_hash}
    return {"status": "ok", "exists": False, "valid": False}


@router.get("/ledger/history/{object_id}")
def ledger_history(object_id: str):
    history = [e for e in LOCAL_LEDGER if e["event"]["object_id"] == object_id]
    return {"status": "ok", "object_id": object_id, "count": len(history), "history": history}

# -----------------------
# Conjunction Assessment + CDM Export
# -----------------------
import uuid
from src.ssa.ca.covariance import CovarianceModel, serialize_covariance
from src.ssa.ca.conjunction import ConjunctionAssessmentEngine
from src.ssa.cdm.cdm_export import export_cdm_xml

_cov_model = CovarianceModel()
_ca_engine = ConjunctionAssessmentEngine()

# In-memory event store (MVP). Later: Postgres.
CONJUNCTION_EVENTS: Dict[str, Dict[str, Any]] = {}

class ConjunctionAssessRequest(BaseModel):
    object1_id: str
    object2_id: str
    window_s: float = Field(default=3600.0, ge=10.0, le=7*24*3600)
    step_s: float = Field(default=10.0, ge=1.0, le=3600.0)
    sigma_pos_km: float = Field(default=0.1, ge=0.001, le=10.0)
    sigma_vel_kms: float = Field(default=0.001, ge=1e-6, le=1.0)
    hard_body_radius_m: float = Field(default=10.0, ge=0.1, le=100.0)

def _latest_fused_state(object_id: str) -> Dict[str, Any]:
    """
    Get a best-effort latest fused state.
    If no fused history, fallback to latest observation across sources.
    """
    if fusion_engine is None:
        raise HTTPException(500, "Fusion engine not initialized")

    # Try fused state
    if getattr(fusion_engine, "fusion_history", None):
        for item in reversed(fusion_engine.fusion_history):
            if item.get("object_id") == object_id:
                return {
                    "position": item["position"],
                    "velocity": item["velocity"]
                }

    # Fallback: latest observation
    latest_obs = None
    for src_name, src in fusion_engine.sources.items():
        for obs in reversed(src.get("observations", [])):
            if obs.get("object_id") == object_id and obs.get("position") and obs.get("velocity"):
                latest_obs = obs
                break
        if latest_obs:
            break

    if latest_obs is None:
        raise HTTPException(status_code=404, detail=f"No state found for object_id={object_id}")

    return {
        "position": latest_obs["position"],
        "velocity": latest_obs["velocity"]
    }

@router.post("/conjunction/assess")
def conjunction_assess(req: ConjunctionAssessRequest):
    # configure HBR
    _ca_engine.hard_body_radius_m = float(req.hard_body_radius_m)

    s1 = _latest_fused_state(req.object1_id)
    s2 = _latest_fused_state(req.object2_id)

    # Init + propagate covariance (MVP: propagate up to window)
    P1 = _cov_model.init_covariance(req.sigma_pos_km, req.sigma_vel_kms)
    P2 = _cov_model.init_covariance(req.sigma_pos_km, req.sigma_vel_kms)

    P1p = _cov_model.propagate(P1, req.window_s)
    P2p = _cov_model.propagate(P2, req.window_s)

    # Find closest approach over window
    ca = _ca_engine.closest_approach(
        {"position": s1["position"], "velocity": s1["velocity"]},
        {"position": s2["position"], "velocity": s2["velocity"]},
        window_s=req.window_s,
        step_s=req.step_s
    )

    # Pc estimation
    pc = _ca_engine.collision_probability(
        miss_distance_km=ca["miss_distance_km"],
        cov1=P1p,
        cov2=P2p
    )

    event_id = "CDM-" + uuid.uuid4().hex[:12].upper()
    tca_utc = datetime.utcnow().isoformat()  # MVP: replace with now+offset later

    event = {
        "event_id": event_id,
        "created_at": datetime.utcnow().isoformat(),
        "tca_utc": tca_utc,
        "miss_distance_km": ca["miss_distance_km"],
        "rel_speed_kms": ca["rel_speed_kms"],
        "pc": pc["pc"],
        "risk": pc["risk"],
        "covariance": {
            "object1": serialize_covariance(P1p),
            "object2": serialize_covariance(P2p)
        },
        "object1": {
            "object_id": req.object1_id,
            "state": s1
        },
        "object2": {
            "object_id": req.object2_id,
            "state": s2
        }
    }

    CONJUNCTION_EVENTS[event_id] = event

    return {
        "status": "ok",
        "event_id": event_id,
        "miss_distance_km": ca["miss_distance_km"],
        "rel_speed_kms": ca["rel_speed_kms"],
        "pc": pc["pc"],
        "risk": pc["risk"],
        "sigma_km": pc["sigma_km"],
        "risk_bubble_km_obj1": _cov_model.risk_radius_km(P1p),
        "risk_bubble_km_obj2": _cov_model.risk_radius_km(P2p),
        "cdm_export_url": f"/ssa/cdm/export/{event_id}"
    }

@router.get("/cdm/export/{event_id}")
def export_cdm(event_id: str):
    if event_id not in CONJUNCTION_EVENTS:
        raise HTTPException(status_code=404, detail="Unknown event_id")
    xml = export_cdm_xml(CONJUNCTION_EVENTS[event_id])

    # Guard: prevent accidental double-CDM concatenation
    if xml.count("<CDM") > 1:
        xml = xml.split("<CDM", 1)[0] + "<CDM" + xml.split("<CDM", 1)[1]
        xml = xml.split("<CDM", 2)[0] + xml.split("<CDM", 2)[1]  # keep first only

    return {
        "status": "ok",
        "event_id": event_id,
        "cdm_xml": xml
    }

# -----------------------
# CDM XML Export (REAL XML Response)
# -----------------------
from fastapi.responses import Response

@router.get("/cdm/export_xml/{event_id}")
def export_cdm_xml_file(event_id: str):
    """
    Return CDM as real XML (application/xml) for download.
    """
    if event_id not in CONJUNCTION_EVENTS:
        raise HTTPException(status_code=404, detail="Unknown event_id")

    xml = export_cdm_xml(CONJUNCTION_EVENTS[event_id])

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={event_id}.xml"
        },
    )

# -----------------------
# CDM XML Export (REAL XML Response) - FIXED
# -----------------------
from fastapi.responses import Response

@router.get("/cdm/export_xml2/{event_id}")
def export_cdm_xml_file_v2(event_id: str):
    """
    Fixed XML endpoint.
    """
    if event_id not in CONJUNCTION_EVENTS:
        raise HTTPException(status_code=404, detail="Unknown event_id")

    xml = export_cdm_xml(CONJUNCTION_EVENTS[event_id])

    # If somehow doubled, keep only first CDM block
    if xml.count("<CDM") > 1:
        first = xml.split("</CDM>", 1)[0] + "</CDM>"
        xml = first

    return Response(
        content=xml,
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={event_id}.xml"
        },
    )
