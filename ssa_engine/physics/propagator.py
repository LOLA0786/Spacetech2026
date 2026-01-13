import numpy as np
from datetime import datetime, timedelta

class OrbitPropagator:
    def __init__(self):
        # Earth gravitational parameter (km^3/s^2)
        self.mu = 398600.4418 

    def simple_propagate(self, position, velocity, duration_seconds):
        """
        A simplified linear-perturbation propagation.
        In a production environment, use SGP4 or Orekit.
        """
        pos = np.array([position['x'], position['y'], position['z']])
        vel = np.array([velocity['vx'], velocity['vy'], velocity['vz']])
        
        # New position: r_f = r_i + v_i*t + 0.5*a*t^2
        # Gravity acceleration a = -mu * r / |r|^3
        r_mag = np.linalg.norm(pos)
        accel = -self.mu * pos / (r_mag**3)
        
        new_pos = pos + vel * duration_seconds + 0.5 * accel * (duration_seconds**2)
        new_vel = vel + accel * duration_seconds
        
        return {
            "x": float(new_pos[0]), "y": float(new_pos[1]), "z": float(new_pos[2]),
            "vx": float(new_vel[0]), "vy": float(new_vel[1]), "vz": float(new_vel[2])
        }
