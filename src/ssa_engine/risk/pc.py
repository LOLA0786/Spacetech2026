import numpy as np

def monte_carlo_pc(primary_state, primary_cov, secondary_state, secondary_cov,
                   num_samples: int = 10000, combined_radius: float = 100.0):
    """
    Monte Carlo collision probability.
    combined_radius: hard-body radius sum (m) — e.g., 50+50 for typical sats.
    """
    # Sample relative state at TCA (or propagate samples if needed)
    rel_state_mean = primary_state - secondary_state
    rel_cov = primary_cov + secondary_cov

    samples = np.random.multivariate_normal(rel_state_mean[:3], rel_cov[:3,:3], num_samples)
    distances = np.linalg.norm(samples, axis=1)
    collisions = distances < combined_radius
    return np.sum(collisions) / num_samples

def alfriend_max_pc(miss_distance: float, combined_radius: float, cov_2d: float):
    """
    Fast analytic upper-bound Pc (Alfriend approximation, 2D encounter plane).
    """
    if miss_distance >= combined_radius:
        return 0.0
    sigma = np.sqrt(cov_2d)
    x = miss_distance / sigma
    r = combined_radius / sigma
    return (r**2 / (2 * np.pi)) * np.exp(-x**2 / 2) * (1 - np.exp(-r**2 / 2))
