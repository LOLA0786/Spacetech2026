import numpy as np

AU = 1.495978707e11  # meters
R_EARTH = 6378137.0
P0 = 4.56e-6  # solar pressure constant at 1 AU (N/m²) for Cr=1 absorption

def get_sun_position(jd: float) -> np.ndarray:
    """
    Low-precision analytical Sun position in ECI (meters).
    Valid 1950–2050, ~0.01° accuracy — perfect for SRP.
    """
    n = jd - 2451545.0
    L = np.deg2rad((280.460 + 0.98564736 * n) % 360)
    g = np.deg2rad((357.528 + 0.98560028 * n) % 360)

    ecl_long = L + np.deg2rad(1.915 * np.sin(g) + 0.020 * np.sin(2 * g))
    ecl_long = ecl_long % (2 * np.pi)

    obliquity = np.deg2rad(23.439 - 0.00000036 * n)

    dist_au = 1.00014 - 0.01671 * np.cos(g) - 0.00014 * np.cos(2 * g)

    x = dist_au * np.cos(ecl_long)
    y = dist_au * np.cos(obliquity) * np.sin(ecl_long)
    z = dist_au * np.sin(obliquity) * np.sin(ecl_long)

    return np.array([x, y, z]) * AU

def conical_eclipse_factor(r_sat: np.ndarray, r_sun: np.ndarray) -> float:
    """
    Simple conical umbra/penumbra approximation (0=full shadow, 1=full sun, linear penumbra).
    """
    au_dist = np.linalg.norm(r_sun)
    if au_dist < AU * 0.5:
        return 1.0
    unit_sun = r_sun / au_dist
    s = np.dot(r_sat, unit_sun)  # projected distance along sun line

    if s > 0:
        return 1.0  # sun-facing side

    perp_vec = r_sat - s * unit_sun
    perp_dist = np.linalg.norm(perp_vec)

    # Umbra cone radius (approx)
    umbra_radius = -s * (R_EARTH / au_dist)
    penumbra_radius = -s * ((R_EARTH + 100000) / au_dist)  # approximate atmosphere

    if perp_dist <= umbra_radius:
        return 0.0
    elif perp_dist <= penumbra_radius:
        return (perp_dist - umbra_radius) / (penumbra_radius - umbra_radius)
    else:
        return 1.0

def srp_acceleration(r_sat: np.ndarray, r_sun: np.ndarray, cr: float = 1.5, area_over_mass: float = 0.02) -> np.ndarray:
    """
    Cannonball SRP acceleration (m/s²). Negative sign on unit_to_sun pushes away from Sun.
    area_over_mass in m²/kg.
    """
    au_dist = np.linalg.norm(r_sun) / AU
    eclipse = conical_eclipse_factor(r_sat, r_sun)

    if eclipse == 0.0 or au_dist < 0.1:
        return np.zeros(3)

    unit_to_sun = r_sun / np.linalg.norm(r_sun)
    pressure = P0 / (au_dist ** 2) * eclipse

    return -pressure * cr * area_over_mass * unit_to_sun
