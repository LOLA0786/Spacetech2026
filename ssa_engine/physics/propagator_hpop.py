import numpy as np

class HighPrecisionPropagator:
    def __init__(self):
        self.mu = 398600.4418  # Earth's gravitational parameter
        self.R_earth = 6378.137 # Earth equatorial radius (km)
        self.J2 = 1.08263e-3   # Second zonal harmonic coefficient

    def propagate(self, pos_dict, vel_dict, dt):
        r = np.array([pos_dict['x'], pos_dict['y'], pos_dict['z']])
        v = np.array([vel_dict['vx'], vel_dict['vy'], vel_dict['vz']])
        
        r_mag = np.linalg.norm(r)
        
        # 1. Basic Two-Body Acceleration
        a_gravity = -self.mu * r / (r_mag**3)
        
        # 2. J2 Perturbation Acceleration
        # This accounts for the Earth's equatorial bulge
        z2 = r[2]**2
        r2 = r_mag**2
        
        factor = (1.5 * self.J2 * self.mu * self.R_earth**2) / (r_mag**5)
        
        a_j2 = np.zeros(3)
        a_j2[0] = factor * r[0] * (5 * (z2 / r2) - 1)
        a_j2[1] = factor * r[1] * (5 * (z2 / r2) - 1)
        a_j2[2] = factor * r[2] * (5 * (z2 / r2) - 3)
        
        # Total Acceleration
        a_total = a_gravity + a_j2
        
        # Update state using Velocity Verlet integration for better stability
        new_pos = r + v * dt + 0.5 * a_total * (dt**2)
        new_vel = v + a_total * dt
        
        return {
            "x": float(new_pos[0]), "y": float(new_pos[1]), "z": float(new_pos[2]),
            "vx": float(new_vel[0]), "vy": float(new_vel[1]), "vz": float(new_vel[2])
        }
