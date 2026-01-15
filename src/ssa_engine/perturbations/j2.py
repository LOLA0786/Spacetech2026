import numpy as np

# Earth gravitational constants (standard WGS84 values)
MU_EARTH = 3.986004418e14      # m³/s²
R_EARTH = 6378137.0            # equatorial radius, m
J2 = 1.082626683e-3            # dimensionless

def j2_acceleration(r_vec: np.ndarray) -> np.ndarray:
    """
    J2 (oblateness) perturbing acceleration in ECI frame.

    Args:
        r_vec: Position vector [x, y, z] in meters (numpy array, shape (3,)).

    Returns:
        Acceleration vector [ax, ay, az] due to J2 in m/s².
    """
    r = np.linalg.norm(r_vec)
    if r < 1000.0:  # avoid singularity at origin
        return np.zeros(3)

    z2_r2 = (r_vec[2] / r) ** 2

    # Common factor (negative sign included)
    factor = - (3.0 * MU_EARTH * J2 * R_EARTH**2) / (2.0 * r**5)

    ax = factor * r_vec[0] * (1.0 - 5.0 * z2_r2)
    ay = factor * r_vec[1] * (1.0 - 5.0 * z2_r2)
    az = factor * r_vec[2] * (3.0 - 5.0 * z2_r2)

    return np.array([ax, ay, az])
