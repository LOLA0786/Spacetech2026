import numpy as np
from .basic import short_arc_tca, numerical_min_distance

def conjunction_pipeline(propagate_func, primary_state, catalog_states, t_span: float = 86400*7,
                        screen_threshold_km: float = 50.0, risk_threshold_m: float = 1000.0):
    """
    Full pipeline:
    - Fast short-arc screening on entire catalog
    - Numerical refinement on candidates
    Returns list of high-risk conjunctions sorted by miss distance.
    catalog_states: list of (id, state[6]) or just states
    """
    candidates = []

    r1, v1 = primary_state[:3], primary_state[3:]

    for idx, secondary_state in catalog_states:
        r2, v2 = secondary_state[:3], secondary_state[3:]

        tca, miss = short_arc_tca(r1, v1, r2, v2)

        if 0 < tca < t_span and miss < screen_threshold_km * 1000:
            precise_tca, precise_miss = numerical_min_distance(propagate_func, primary_state, secondary_state, t_span)

            if precise_miss < risk_threshold_m:
                candidates.append({
                    'object_id': idx,
                    'tca_seconds': precise_tca,
                    'miss_distance_m': precise_miss,
                    'relative_velocity': np.linalg.norm(v1 - v2)
                })

    candidates.sort(key=lambda x: x['miss_distance_m'])
    return candidates
