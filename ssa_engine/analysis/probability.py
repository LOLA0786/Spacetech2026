import numpy as np

class ProbabilityEngine:
    @staticmethod
    def calculate_pc(distance_km, sigma_combined=0.1):
        """
        A simplified Gaussian probability model.
        In reality, this involves integrating the 3D covariance.
        """
        # Pc = exp(-0.5 * (d^2 / sigma^2))
        if distance_km > 50:
            return 0.0
        
        exponent = -0.5 * (distance_km**2 / sigma_combined**2)
        pc = np.exp(exponent)
        
        return round(float(pc), 8)
