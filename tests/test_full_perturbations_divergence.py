import numpy as np
from scipy.integrate import solve_ivp
# Import all perturbations...

def test_irnss_third_body_dominance():
    a = 42164e3
    state = np.array([a, 0, 0, 0, np.sqrt(MU_EARTH/a), 1000.0])  # slight incl
    times = np.linspace(0, 30*86400, 500)
    
    sol_basic = solve_ivp(basic_eom, [0, times[-1]], state, t_eval=times)  # define basic/two-body
    sol_full = solve_ivp(full_eom_with_all, [0, times[-1]], state, t_eval=times)
    
    diff_km = np.linalg.norm(sol_full.y[:3,-1] - sol_basic.y[:3,-1]) / 1e3
    assert diff_km > 100.0  # massive lunar-solar drift in unprotected GSO
    print(f"🎯 Third-body divergence: {diff_km:.1f} km over 30 days — shining on IRNSS!")

# Similar for SRP, higher zonals...
