import numpy as np
from dataclasses import dataclass
from typing import Dict

@dataclass
class CovarianceModel:
    """
    Dynamic covariance propagation (MVP).

    State: [x y z vx vy vz]^T
    Covariance: 6x6 matrix P

    We use a simple constant-velocity state transition:
      x' = x + vx*dt
      v' = v

    And add process noise Q to allow "risk bubble" growth.
    """

    # Process noise parameters (tune later)
    sigma_pos_km: float = 0.05     # km
    sigma_vel_kms: float = 0.0001  # km/s

    def init_covariance(self,
                        sigma_pos_km: float = 0.1,
                        sigma_vel_kms: float = 0.001) -> np.ndarray:
        P = np.zeros((6,6), dtype=float)
        P[0,0] = sigma_pos_km**2
        P[1,1] = sigma_pos_km**2
        P[2,2] = sigma_pos_km**2
        P[3,3] = sigma_vel_kms**2
        P[4,4] = sigma_vel_kms**2
        P[5,5] = sigma_vel_kms**2
        return P

    def propagate(self, P: np.ndarray, dt_s: float) -> np.ndarray:
        # State transition F for constant velocity
        F = np.eye(6, dtype=float)
        F[0,3] = dt_s
        F[1,4] = dt_s
        F[2,5] = dt_s

        # Process noise Q (simple diagonal growth)
        q_pos = (self.sigma_pos_km**2) * max(dt_s, 1.0)
        q_vel = (self.sigma_vel_kms**2) * max(dt_s, 1.0)
        Q = np.zeros((6,6), dtype=float)
        Q[0,0] = q_pos
        Q[1,1] = q_pos
        Q[2,2] = q_pos
        Q[3,3] = q_vel
        Q[4,4] = q_vel
        Q[5,5] = q_vel

        P2 = F @ P @ F.T + Q
        return P2

    def risk_radius_km(self, P: np.ndarray, sigma: float = 3.0) -> float:
        """
        Risk bubble radius from position covariance.
        Use 3-sigma by default.
        """
        pos_var = float(P[0,0] + P[1,1] + P[2,2]) / 3.0
        std = np.sqrt(max(pos_var, 0.0))
        return float(sigma * std)

def serialize_covariance(P: np.ndarray) -> Dict:
    return {"matrix": P.tolist()}

def deserialize_covariance(obj: Dict) -> np.ndarray:
    return np.array(obj["matrix"], dtype=float)
