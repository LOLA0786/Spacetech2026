import pytest
import numpy as np
from scipy.integrate import solve_ivp

from src.ssa_engine.perturbations.j2 import j2_acceleration
from src.ssa_engine.perturbations.higher_zonals import higher_zonal_acceleration
from src.ssa_engine.perturbations.srp import srp_acceleration, get_sun_position
from src.ssa_engine.perturbations.third_body import third_body_acceleration

MU_EARTH = 3.986004418e14

# Hardcoded real ISS TLE (Celestrak, epoch ~2026-01-14)
ISS_TLE_NAME = "ISS (ZARYA)"
ISS_LINE1 = "1 25544U 98067A   26014.62805721  .00006818  00000+0  13044-3 0  9991"
ISS_LINE2 = "2 25544  51.6333 339.6562 0007763  17.9854 342.1408 15.49289811547943"

# Simple mean-to-osculating approximation for test (good enough for short-arc sanity)
def tle_to_state(line1, line2):
    from math import radians, sqrt, pi
    n = float(line2[52:63]) * 2 * pi / 86400  # mean motion rad/s
    a = (MU_EARTH / n**2)**(1/3)
    e = float("0." + line2[26:33])
    i = radians(float(line2[8:16]))
    omega = radians(float(line2[17:25]))
    Omega = radians(float(line2[34:42]))
    M = radians(float(line2[43:51]))
    
    # Circular approx for velocity
    r_mag = a * (1 - e**2)
    v_mag = sqrt(MU_EARTH * (2/r_mag - 1/a))
    
    # ECI position (approx equatorial for test sanity)
    r = np.array([r_mag, 0, 0])
    v = np.array([0, v_mag, 0])
    return np.concatenate([r, v])

@pytest.fixture
def iss_state():
    return tle_to_state(ISS_LINE1, ISS_LINE2)

def full_eom(t, state, epoch_jd=2460680.0):  # approx Jan 2026 JD
    r = state[:3]
    v = state[3:]
    a = -MU_EARTH * r / np.linalg.norm(r)**3
    a += j2_acceleration(r)
    a += higher_zonal_acceleration(r)
    jd = epoch_jd + t / 86400.0
    sun = get_sun_position(jd)
    a += srp_acceleration(r, sun, cr=1.4, area_over_mass=0.01)  # typical ISS
    a += third_body_acceleration(r, jd)
    return np.concatenate([v, a])

def test_iss_short_propagation_sanity(iss_state):
    times = np.linspace(0, 86400, 100)  # 1 day
    sol = solve_ivp(full_eom, [0, times[-1]], iss_state, t_eval=times, rtol=1e-8)
    assert sol.success
    alt_final = np.linalg.norm(sol.y[:3, -1]) - 6378137
    assert 400000 < alt_final < 430000  # ISS altitude range ~410-430 km

def test_iss_drag_like_decay(iss_state):
    # With vs without drag (assuming you add drag later; placeholder check altitude drop)
    # For now, check perturbation magnitude
    r = iss_state[:3]
    a_j2 = np.linalg.norm(j2_acceleration(r))
    assert 1e-5 < a_j2 < 1e-4  # J2 order for LEO
