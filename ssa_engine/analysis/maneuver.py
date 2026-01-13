import numpy as np
from copy import deepcopy

class ManeuverEngine:
    def __init__(self, propagator, safe_distance_km=2.0):
        self.propagator = propagator
        self.safe_distance = safe_distance_km

    def calculate_avoidance(self, state, debris_pos, duration_secs):
        """
        Attempts to find a Delta-V burn that clears the debris.
        """
        # We try small increments of Delta-V in the velocity direction (Prograde)
        for dv_magnitude in [0.001, 0.005, 0.01, 0.05]: # km/s
            temp_vel = deepcopy(state['velocity'])
            
            # Apply burn: Normalize velocity vector and multiply by DV
            v_vec = np.array([temp_vel['vx'], temp_vel['vy'], temp_vel['vz']])
            v_unit = v_vec / np.linalg.norm(v_vec)
            new_v_vec = v_vec + (v_unit * dv_magnitude)
            
            new_vel = {"vx": new_v_vec[0], "vy": new_v_vec[1], "vz": new_v_vec[2]}
            
            # Predict new path with this burn
            future_state = self.propagator.simple_propagate(state['position'], new_vel, duration_secs)
            
            # Check new distance
            pos_a = np.array([future_state['x'], future_state['y'], future_state['z']])
            pos_b = np.array([debris_pos['x'], debris_pos['y'], debris_pos['z']])
            new_distance = np.linalg.norm(pos_a - pos_b)
            
            if new_distance > self.safe_distance:
                return {
                    "recommended_dv_kms": dv_magnitude,
                    "new_miss_distance_km": float(new_distance),
                    "burn_direction": "Prograde"
                }
        
        return {"error": "Could not find a safe maneuver within fuel limits"}
