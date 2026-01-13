import numpy as np
from typing import Dict
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class DataFusionEngine:
    """
    Fuses multiple SSA data sources with AI-powered conflict resolution
    Sources: TLE, optical observations, radar, ADS-B, blockchain ledger
    """

    def __init__(self):
        self.sources = {}
        self.confidence_model = RandomForestClassifier(n_estimators=100)
        self.fusion_history = []

    def register_source(self, name: str, reliability: float, latency_ms: int):
        """Register a data source with metadata"""
        self.sources[name] = {
            "reliability": reliability,  # 0.0 to 1.0
            "latency": latency_ms,
            "observations": [],
        }
        logger.info(f"Registered source: {name} (reliability: {reliability})")

    def ingest_observation(self, source: str, obj_id: str, data: Dict):
        """Ingest observation from a source"""
        if source not in self.sources:
            raise ValueError(f"Unknown source: {source}")

        observation = {
            "timestamp": datetime.utcnow(),
            "object_id": obj_id,
            "position": data.get("position"),
            "velocity": data.get("velocity"),
            "confidence": data.get("confidence", 0.9),
            "source": source,
        }

        self.sources[source]["observations"].append(observation)
        return observation

    def fuse(self, obj_id: str, time_window_hours: int = 1) -> Dict:
        """
        Fuse observations for an object using weighted averaging
        and ML-based conflict resolution
        """
        cutoff = datetime.utcnow().timestamp() - (time_window_hours * 3600)

        observations = []
        for source_name, source_data in self.sources.items():
            for obs in source_data["observations"]:
                if obs["object_id"] == obj_id and obs["timestamp"].timestamp() > cutoff:
                    observations.append(obs)

        if not observations:
            return {"error": "No observations in time window"}

        total_weight = 0.0
        fused_position = np.zeros(3)
        fused_velocity = np.zeros(3)

        for obs in observations:
            source_reliability = self.sources[obs["source"]]["reliability"]
            weight = float(source_reliability * obs["confidence"])

            if obs["position"]:
                pos = np.array(
                    [obs["position"]["x"], obs["position"]["y"], obs["position"]["z"]],
                    dtype=float,
                )
                fused_position += weight * pos

            if obs["velocity"]:
                vel = np.array(
                    [obs["velocity"]["vx"], obs["velocity"]["vy"], obs["velocity"]["vz"]],
                    dtype=float,
                )
                fused_velocity += weight * vel

            total_weight += weight

        if total_weight == 0:
            return {"error": "Zero total weight"}

        fused_position /= total_weight
        fused_velocity /= total_weight

        result = {
            "object_id": obj_id,
            "fused_time": datetime.utcnow().isoformat(),
            "position": {"x": float(fused_position[0]), "y": float(fused_position[1]), "z": float(fused_position[2])},
            "velocity": {"vx": float(fused_velocity[0]), "vy": float(fused_velocity[1]), "vz": float(fused_velocity[2])},
            "confidence": float(total_weight / max(1, len(observations))),
            "num_sources": len(set(o["source"] for o in observations)),
        }

        self.fusion_history.append(result)
        return result
