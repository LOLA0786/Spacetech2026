import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Tuple
import math

@dataclass
class ConjunctionAssessmentEngine:
    """
    MVP Conjunction Assessment:
    - Closest approach over time window using coarse sampling
    - Probability of collision Pc approximation using miss distance + combined covariance

    This is NOT final NASA-grade Pc yet.
    It is operational MVP that is consistent and monotonic.
    """

    hard_body_radius_m: float = 10.0  # combined HBR default (m)

    def _vec(self, p: Dict[str, float]) -> np.ndarray:
        return np.array([p["x"], p["y"], p["z"]], dtype=float)

    def _vvec(self, v: Dict[str, float]) -> np.ndarray:
        return np.array([v["vx"], v["vy"], v["vz"]], dtype=float)

    def closest_approach(self,
                         state1: Dict[str, Any],
                         state2: Dict[str, Any],
                         window_s: float = 3600.0,
                         step_s: float = 10.0) -> Dict[str, Any]:
        """
        state:
          position: {x,y,z} km
          velocity: {vx,vy,vz} km/s
        """

        p10 = self._vec(state1["position"])
        v10 = self._vvec(state1["velocity"])
        p20 = self._vec(state2["position"])
        v20 = self._vvec(state2["velocity"])

        best = {
            "t_offset_s": 0.0,
            "miss_distance_km": float("inf"),
            "rel_speed_kms": 0.0,
            "p1_km": p10.tolist(),
            "p2_km": p20.tolist(),
        }

        t = 0.0
        while t <= window_s:
            p1 = p10 + v10 * t
            p2 = p20 + v20 * t
            rel = p2 - p1
            miss = float(np.linalg.norm(rel))
            if miss < best["miss_distance_km"]:
                best["t_offset_s"] = float(t)
                best["miss_distance_km"] = miss
                best["rel_speed_kms"] = float(np.linalg.norm(v20 - v10))
                best["p1_km"] = p1.tolist()
                best["p2_km"] = p2.tolist()
            t += step_s

        return best

    def collision_probability(self,
                              miss_distance_km: float,
                              cov1: np.ndarray,
                              cov2: np.ndarray) -> Dict[str, Any]:
        """
        Approx Pc model:
        - combine position covariances
        - compute sigma (km)
        - Pc ~ exp(-(d^2)/(2*sigma^2)) scaled by HBR

        This is a conservative monotonic approximation.
        """
        # combine covariance for relative position (3x3)
        Ppos1 = cov1[0:3, 0:3]
        Ppos2 = cov2[0:3, 0:3]
        P = Ppos1 + Ppos2

        # isotropic sigma from trace
        sigma2 = float(np.trace(P) / 3.0)
        sigma = math.sqrt(max(sigma2, 1e-12))

        # hard body radius in km
        hbr_km = float(self.hard_body_radius_m / 1000.0)

        d = float(miss_distance_km)

        # base probability
        base = math.exp(-(d * d) / (2.0 * sigma * sigma))

        # scale by ratio of cross section to uncertainty circle
        scale = min(1.0, (hbr_km / max(sigma, 1e-9))**2)
        pc = float(min(1.0, base * scale))

        risk = "LOW"
        if pc >= 1e-3:
            risk = "CRITICAL"
        elif pc >= 1e-4:
            risk = "HIGH"
        elif pc >= 1e-6:
            risk = "MEDIUM"

        return {
            "pc": pc,
            "risk": risk,
            "sigma_km": float(sigma),
            "hbr_km": hbr_km
        }
