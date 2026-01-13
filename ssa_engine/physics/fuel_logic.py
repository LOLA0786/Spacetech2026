class FuelCalculator:
    def __init__(self, total_fuel_capacity_kg=50.0):
        self.capacity = total_fuel_capacity_kg
        self.g0 = 0.00981 # km/s^2 (Standard gravity in km)

    def estimate_cost(self, satellite_mass_kg, dv_kms):
        """
        Uses the Tsiolkovsky Rocket Equation to find fuel mass used.
        m_fuel = m0 * (1 - e^(-dv / (g * Isp)))
        """
        isp = 300 # Specific Impulse in seconds
        ve = isp * self.g0
        
        # Calculate fuel consumed
        fuel_consumed = satellite_mass_kg * (1 - (2.71828 ** (-dv_kms / ve)))
        
        # Estimate mission life impact (Assuming 50kg = 15 years of life)
        years_per_kg = 15 / self.capacity
        life_lost_days = fuel_consumed * years_per_kg * 365
        
        return {
            "fuel_consumed_kg": round(float(fuel_consumed), 4),
            "mission_life_lost_days": round(float(life_lost_days), 2),
            "remaining_fuel_est_kg": round(float(self.capacity - fuel_consumed), 2)
        }
