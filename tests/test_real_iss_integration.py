import pytest
import numpy as np
from scipy.integrate import solve_ivp
from math import radians, pi

from src.ssa_engine.perturbations.j2 import j2_acceleration
from src.ssa_engine.perturbations.higher_zonals import higher_zonal_acceleration
from src.ssa_engine.perturbations.srp import srp_acceleration, get_sun_position
from src.ssa_engine.perturbations.third_body import third_body_acceleration

MU_EARTH = 3.986004418e14
R_EARTH = 6378137.0

# Real ISS TLE from Celestrak (epoch ~Jan 14-15 2026)
ISS_LINE1 = "1 25544U 98067A   26014.62805721  .00006818  00000+0  13044-3 0  9991"
ISS_LINE2 = "2 25544  51.6333 339.6562 0007763  17.9854 342.1408 15.49289811547943"

def parse_tle_to_osculating():
    n_rev_day = float(ISS_LINE2[52:63])
    n = n_rev_day * 2 * pi / 86400.0
    a = (MU_EARTH / n**2)**(1/3)
    e = float("0." + ISS_LINE2[26:33])
    i = radians(float(ISS_LINE2[8:16]))
    
    r_mag = a * (1 - e**2)
    v_mag = np.sqrt(MU_EARTH * (2/r_mag - 1/a))
    
    # Rough ECI state (perigee-aligned, inclination applied)
    r = r_mag * np.array([1.0, 0.0, 0.0])
    v = v_mag * np.array([0.0, np.cos(i), np.sin(i)])
    return np.concatenate([r, v])

@pytest.fixture
def iss_state():
    return parse_tle_to_osculating()

def full_eom(t, state, epoch_jd=2460680.5):
    r = state[:3]
    v = state[3:]
    a = -MU_EARTH * r / np.linalg.norm(r)**3
    a += j2_acceleration(r)
    a += higher_zonal_acceleration(r)
    jd = epoch_jd + t / 86400.0
    sun = get_sun_position(jd)
    a += srp_acceleration(r, sun, cr=1.4, area_over_mass=0.012)
    a += third_body_acceleration(r, jd)
    return np.concatenate([v, a])

def test_iss_propagation_sanity(iss_state):
    times = np.linspace(0, 86400*3, 500)  # 3 days
    sol = solve_ivp(full_eom, [0, times[-1]], iss_state, t_eval=times, rtol=1e-9, atol=1e-9)
    assert sol.success
    altitudes = np.linalg.norm(sol.y[:3], axis=0) - R_EARTH
    mean_alt_km = np.mean(altitudes) / 1000
    assert 400 < mean_alt_km < 430
    print(f"ISS 3-day mean altitude: {mean_alt_km:.1f} km — matches expected range")

def test_perturbation_magnitudes(iss_state):
    r = iss_state[:3]
    assert 1e-5 < np.linalg.norm(j2_acceleration(r)) < 1e-4
    jd = 2460680.5
    assert np.linalg.norm(third_body_acceleration(r, jd)) < 1e-6  # smaller in LEO
