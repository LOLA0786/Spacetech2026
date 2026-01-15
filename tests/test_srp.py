import numpy as np
from scipy.integrate import solve_ivp
from src.ssa_engine.perturbations.srp import get_sun_position, conical_eclipse_factor, srp_acceleration

MU_EARTH = 3.986004418e14

def test_srp_eclipse():
    r_sat = np.array([0, 0, -7000000.0])  # anti-sun side
    r_sun = get_sun_position(2460680.0)
    eclipse = conical_eclipse_factor(r_sat, r_sun)
    assert 0.0 <= eclipse <= 0.2  # deep shadow or penumbra

    r_sat_sunside = np.array([7000000.0, 0, 0])
    eclipse_sun = conical_eclipse_factor(r_sat_sunside, r_sun)
    assert eclipse_sun == 1.0

def test_srp_acceleration():
    r = np.array([7000000.0, 0, 0])
    r_sun = get_sun_position(2460680.0)
    a_srp = srp_acceleration(r, r_sun, cr=1.5, area_over_mass=0.02)
    mag = np.linalg.norm(a_srp)
    assert 1e-8 < mag < 1e-7  # typical LEO/GSO SRP order
