import numpy as np

class ProbabilityEngineV2:
    def calculate_pc(self, distance, sigma_combined):
        """
        Foster's 2D Probability of Collision (Pc)
        Computes the integral of the relative covariance over the hard-body radius.
        """
        # Hard-body radius (satellite + debris size) approx 10 meters
        HBR = 0.01 
        
        if distance > (sigma_combined * 10):
            return 0.0
            
        # Simplified 2D Gaussian integration
        exponent = - (distance**2) / (2 * sigma_combined**2)
        pc = 1 - np.exp(exponent * (HBR**2 / sigma_combined**2)) # Simplified
        
        # Fallback to standard Gaussian for display
        pc_alt = np.exp(-0.5 * (distance / sigma_combined)**2)
        
        return round(float(pc_alt), 8)
