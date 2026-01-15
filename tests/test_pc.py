import numpy as np
from src.ssa_engine.risk.pc import monte_carlo_pc, alfriend_max_pc

def test_monte_carlo_pc():
    # Synthetic close approach: 500m miss, 100m combined radius, small cov
    rel_pos = np.array([500.0, 0, 0])
    rel_cov = np.diag([100.0**2, 100.0**2, 50.0**2])
    primary_cov = rel_cov / 2
    secondary_cov = rel_cov / 2
    primary_state = np.concatenate([rel_pos/2, np.zeros(3)])
    secondary_state = np.concatenate([-rel_pos/2, np.zeros(3)])

    pc = monte_carlo_pc(primary_state, primary_cov, secondary_state, secondary_cov,
                        num_samples=50000, combined_radius=100.0)
    assert 0.0 < pc < 0.1  # low but non-zero probability

def test_alfriend_upper_bound():
    pc_max = alfriend_max_pc(miss_distance=500.0, combined_radius=100.0, cov_2d=10000.0)  # sigma~100m
    assert pc_max > 0.0
