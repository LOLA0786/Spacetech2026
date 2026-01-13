import numpy as np

class ConjunctionEngine:
    def __init__(self, collision_threshold_km=10.0):
        self.threshold = collision_threshold_km

    def check_close_approach(self, object_a_state, debris_catalog):
        """
        Compares object_a against a list of debris objects.
        """
        risks = []
        pos_a = np.array([object_a_state['x'], object_a_state['y'], object_a_state['z']])
        
        for debris in debris_catalog:
            pos_b = np.array([debris['x'], debris['y'], debris['z']])
            distance = np.linalg.norm(pos_a - pos_b)
            
            if distance < self.threshold:
                risks.append({
                    "debris_id": debris['id'],
                    "distance_km": float(distance),
                    "risk_level": "CRITICAL" if distance < 2.0 else "WARNING"
                })
        
        return risks
