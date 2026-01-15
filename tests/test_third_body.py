import pytest
import numpy as np
from scipy.integrate import solve_ivp

from src.ssa_engine.perturbations.third_body import get_sun_position, get_moon_position, third_body_acceleration

MU_EARTH = 3.986004418e14
R_EARTH = 6378137.0

@pytest.fixture
def irnss_like_state():
    # Synthetic IRNSS/NVS-like GSO: circular equatorial ~42,164 km (real TLE mean motion ~1.0027 rev/day)
    a = 42164e3  # meters
    r0 = a * np.array([1.0, 0.0, 0.0])
    v_mag = np.sqrt(MU_EARTH / a)
    v0 = v_mag * np.array([0.0, 1.0, 0.0])
    return np.concatenate([r0, v0])

def equations_of_motion(t, state, include_third_body=False, epoch_jd=2460680.0):  # approx Jan 2026
    r = state[:3]
    v = state[3:]
    a = -MU_EARTH * r / np.linalg.norm(r)**3
    if include_third_body:
        jd = epoch_jd + t / 86400.0
        a += third_body_acceleration(r, jd)
    return np.concatenate([v, a])

def test_sun_moon_positions():
    jd = 2460680.0  # mid-Jan 2026 approx
    sun = get_sun_position(jd)
    moon = get_moon_position(jd)
    assert 0.98 * 1.495978707e11 < np.linalg.norm(sun) < 1.02 * 1.495978707e11
    assert 3.5e8 < np.linalg.norm(moon) < 4.1e8  # ~384,000 km average

def test_third_body_acceleration_magnitude(irnss_like_state):
    r = irnss_like_state[:3]
    jd = 2460680.0
    a_tb = third_body_acceleration(r, jd)
    mag = np.linalg.norm(a_tb)
    assert 5e-7 < mag < 5e-6  # expected lunar-solar order for GSO (moon dominant in some configs)

def test_third_body_propagation_divergence(irnss_like_state):
    times = np.linspace(0, 30 * 86400, 1000)  # 30 days
    epoch_jd = 2460680.0

    # Two-body only (should stay nearly circular)
    sol_tb_off = solve_ivp(equations_of_motion, [0, times[-1]], irnss_like_state,
                           args=(False, epoch_jd), t_eval=times, rtol=1e-9, atol=1e-9)
    
    # With third-body
    sol_tb_on = solve_ivp(equations_of_motion, [0, times[-1]], irnss_like_state,
                          args=(True, epoch_jd), t_eval=times, rtol=1e-9, atol=1e-9)

    final_diff = np.linalg.norm(sol_tb_on.y[:3, -1] - sol_tb_off.y[:3, -1]) / 1e3  # km
    assert final_diff > 50.0  # expect >50 km divergence over 30 days due to lunar-solar drift (realistic for unprotected GSO)
    assert sol_tb_on.success and sol_tb_off.success
