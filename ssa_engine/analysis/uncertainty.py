import numpy as np

class UncertaintyEngine:
    def __init__(self):
        # Initial standard deviation in km (position) and km/s (velocity)
        self.initial_sigma_pos = 0.5 
        self.initial_sigma_vel = 0.001

    def get_covariance_at_time(self, dt_seconds):
        """
        Predicts how the 6x6 covariance matrix grows over time.
        For simplicity, we model the growth of the 'Risk Bubble' radius.
        """
        # Uncertainty grows linearly with time due to velocity errors
        # Growth Rate: approx 100 meters per hour for LEO
        growth_factor = 0.00003  # km per second
        
        current_sigma = self.initial_sigma_pos + (growth_factor * dt_seconds)
        
        # In a real system, this would be a 6x6 matrix:
        # P_t = Phi * P_0 * Phi^T + Q
        return {
            "sigma_km": round(float(current_sigma), 4),
            "bubble_volume_km3": round(float((4/3) * np.pi * (current_sigma**3)), 6)
        }
