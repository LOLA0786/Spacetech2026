class ManeuverExecutor:
    @staticmethod
    def apply_burn(current_velocity, dv_magnitude):
        """
        Applies a prograde burn to the velocity vector.
        """
        import numpy as np
        v_vec = np.array([current_velocity['vx'], current_velocity['vy'], current_velocity['vz']])
        v_unit = v_vec / np.linalg.norm(v_vec)
        
        # New velocity = old velocity + (direction * magnitude)
        new_v_vec = v_vec + (v_unit * dv_magnitude)
        
        return {
            "vx": float(new_v_vec[0]),
            "vy": float(new_v_vec[1]),
            "vz": float(new_v_vec[2])
        }
