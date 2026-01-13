import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Detect unusual satellite maneuvers using Isolation Forest
    Flags: unreported maneuvers, ASAT threats, debris creation events
    """

    def __init__(self, contamination=0.01):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=200,
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def extract_features(self, trajectory: List[Dict]) -> np.ndarray:
        """Extract features from trajectory history"""
        if len(trajectory) < 3:
            raise ValueError("Need at least 3 positions for features")

        features = []

        for i in range(1, len(trajectory)):
            prev = trajectory[i - 1]
            curr = trajectory[i]

            dx = curr["position"]["x"] - prev["position"]["x"]
            dy = curr["position"]["y"] - prev["position"]["y"]
            dz = curr["position"]["z"] - prev["position"]["z"]

            dvx = curr["velocity"]["vx"] - prev["velocity"]["vx"]
            dvy = curr["velocity"]["vy"] - prev["velocity"]["vy"]
            dvz = curr["velocity"]["vz"] - prev["velocity"]["vz"]

            dt = (curr["timestamp"] - prev["timestamp"]).total_seconds()

            ax = dvx / dt if dt > 0 else 0
            ay = dvy / dt if dt > 0 else 0
            az = dvz / dt if dt > 0 else 0

            features.append([dx, dy, dz, dvx, dvy, dvz, ax, ay, az])

        return np.array(features, dtype=float)

    def train(self, normal_trajectories: List[List[Dict]]):
        """Train on known normal behavior"""
        logger.info(f"Training on {len(normal_trajectories)} trajectories")

        all_features = []
        for traj in normal_trajectories:
            try:
                features = self.extract_features(traj)
                all_features.extend(list(features))
            except ValueError:
                continue

        X = np.array(all_features, dtype=float)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

        logger.info("Training complete")

    def detect(self, trajectory: List[Dict]) -> Dict:
        """Detect anomalies in trajectory"""
        if not self.is_trained:
            raise RuntimeError("Model not trained")

        features = self.extract_features(trajectory)
        X_scaled = self.scaler.transform(features)

        predictions = self.model.predict(X_scaled)  # -1 anomaly, 1 normal
        scores = self.model.score_samples(X_scaled)

        anomaly_indices = np.where(predictions == -1)[0]

        result = {
            "is_anomalous": bool(len(anomaly_indices) > 0),
            "anomaly_count": int(len(anomaly_indices)),
            "anomaly_times": [trajectory[i + 1]["timestamp"].isoformat() for i in anomaly_indices],
            "min_score": float(np.min(scores)),
            "mean_score": float(np.mean(scores)),
            "risk_level": self._calculate_risk(scores),
        }

        return result

    def _calculate_risk(self, scores: np.ndarray) -> str:
        """Calculate risk level from anomaly scores"""
        min_score = float(np.min(scores))
        if min_score < -0.5:
            return "CRITICAL"
        elif min_score < -0.3:
            return "HIGH"
        elif min_score < -0.1:
            return "MEDIUM"
        else:
            return "LOW"

    def save(self, path: str):
        """Save trained model"""
        joblib.dump(
            {
                "model": self.model,
                "scaler": self.scaler,
                "is_trained": self.is_trained,
            },
            path,
        )
        logger.info(f"Model saved to {path}")

    def load(self, path: str):
        """Load trained model"""
        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = data["is_trained"]
        logger.info(f"Model loaded from {path}")
