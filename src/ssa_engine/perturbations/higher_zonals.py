import numpy as np

MU_EARTH = 3.986004418e14
R_EARTH = 6378137.0
J3 = -2.532717e-6   # standard value
J4 = -1.6196219e-6  # standard value

def higher_zonal_acceleration(r_vec: np.ndarray, include_j3: bool = True, include_j4: bool = True) -> np.ndarray:
    """
    Combined J3 + J4 perturbing acceleration (m/s²). Valid above ~100 km altitude.
    Formulas matched to common high-fidelity implementations (Vallado-style, unnormalized).
    """
    a = np.zeros(3)
    r = np.linalg.norm(r_vec)
    if r < R_EARTH + 100000.0:  # avoid low-altitude/singularity issues
        return a

    x, y, z = r_vec
    z2 = z**2
    r2 = r**2
    r4 = r2**2

    if include_j3:
        factor = 3.0 * MU_EARTH * J3 * R_EARTH**3 * z / (2.0 * r**7)
        common = (5.0 * z2 / r2 - 1.0)
        a[0] += factor * x * common
        a[1] += factor * y * common
        a[2] += factor * z * (5.0 * z2 / r2 - 3.0)

    if include_j4:
        factor = -5.0 * MU_EARTH * J4 * R_EARTH**4 / (8.0 * r**9)
        common = (35.0 * z**4 / r4 - 30.0 * z2 / r2 + 3.0)
        a[0] += factor * x * common
        a[1] += factor * y * common
        a[2] += factor * z * (35.0 * z**4 / r4 - 30.0 * z2 / r2 + 3.0)

    return a
