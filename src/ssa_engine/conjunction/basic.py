import numpy as np
from scipy.optimize import minimize_scalar

# Fast analytic short-arc conjunction (assumes straight-line relative motion)
def short_arc_tca(r1: np.ndarray, v1: np.ndarray,
                  r2: np.ndarray, v2: np.ndarray):
    """
    Compute time of closest approach and miss distance using constant relative velocity.

    Valid for short propagation arcs (< ~1 day in LEO).

    Args:
        r1, v1: position and velocity of primary object (m, m/s)
        r2, v2: position and velocity of secondary object

    Returns:
        tca (s): time to closest approach (positive = future)
        miss_distance (m)
    """
    rel_r = r1 - r2
    rel_v = v1 - v2

    rv_dot = np.dot(rel_r, rel_v)
    v2 = np.dot(rel_v, rel_v)

    if v2 < 1e-8:  # almost zero relative velocity
        return 0.0, np.linalg.norm(rel_r)

    t_tca = -rv_dot / v2

    rel_r_tca = rel_r + t_tca * rel_v
    miss_dist = np.linalg.norm(rel_r_tca)

    return t_tca, miss_dist


# Numerical refinement (uses full HPOP propagation)
def numerical_min_distance(propagate_func, state1, state2,
                           t_span: float, num_coarse: int = 500):
    """
    Find precise TCA and minimum distance using coarse grid + scalar minimization.

    Args:
        propagate_func: function that takes state [r,v] and array of times → positions (N,3)
        state1, state2: initial states [rx,ry,rz,vx,vy,vz]
        t_span: propagation length in seconds (future only)
        num_coarse: points for initial coarse search

    Returns:
        tca (s), min_distance (m)
    """
    times_coarse = np.linspace(0, t_span, num_coarse)
    pos1 = propagate_func(state1, times_coarse)
    pos2 = propagate_func(state2, times_coarse)

    rel_dist = np.linalg.norm(pos1 - pos2, axis=1)
    idx_min = np.argmin(rel_dist)
    t_coarse_min = times_coarse[idx_min]

    # Refine around coarse minimum
    def distance_at_t(t):
        p1 = propagate_func(state1, np.array([t]))[0]
        p2 = propagate_func(state2, np.array([t]))[0]
        return np.linalg.norm(p1 - p2)

    res = minimize_scalar(distance_at_t,
                          bounds=(max(0, t_coarse_min - t_span/10),
                                  min(t_span, t_coarse_min + t_span/10)),
                          tol=0.1)

    return res.x, res.fun
