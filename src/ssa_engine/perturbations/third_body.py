import numpy as np

MU_SUN = 1.3271244e20
MU_MOON = 4.9048695e12
AU = 1.495978707e11

# Reuse low-precision Sun from SRP (moved here for shared use)
def get_sun_position(jd: float) -> np.ndarray:
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

# Low-precision analytical Moon (~1-2 km accuracy, sufficient for perturbation)
def get_moon_position(jd: float) -> np.ndarray:
    T = (jd - 2451545.0) / 36525.0
    L0 = np.deg2rad(218.31617 + 481267.8813 * T) % (2*np.pi)
    l = np.deg2rad(134.96292 + 477198.8676 * T) % (2*np.pi)
    lp = np.deg2rad(357.52577 + 35999.0503 * T) % (2*np.pi)
    F = np.deg2rad(93.27209 + 483202.0175 * T) % (2*np.pi)
    D = np.deg2rad(297.85019 + 445267.1115 * T) % (2*np.pi)

    dist = 385000e3 * (1 - 0.0167 * np.cos(l - lp))  # approximate km to m

    lon = L0 + np.deg2rad(6.289 * np.sin(l) + 1.274 * np.sin(2*D - l))
    lat = np.deg2rad(5.128 * np.sin(F))

    x = dist * np.cos(lat) * np.cos(lon)
    y = dist * np.cos(lat) * np.sin(lon) * np.cos(np.deg2rad(23.439))
    z = dist * (np.sin(lat) * np.cos(np.deg2rad(23.439)) + np.cos(lat) * np.sin(lon) * np.sin(np.deg2rad(23.439)))

    return np.array([x, y, z])

def third_body_acceleration(r_sat: np.ndarray, jd: float, include_sun: bool = True, include_moon: bool = True) -> np.ndarray:
    a = np.zeros(3)
    r3 = np.linalg.norm(r_sat)**3

    if include_sun:
        r_sun = get_sun_position(jd)
        r_sun_sat = r_sat - r_sun
        r_sun3 = np.linalg.norm(r_sun_sat)**3
        r_sun_norm3 = np.linalg.norm(r_sun)**3
        a += MU_SUN * (r_sun_sat / r_sun3 - r_sun / r_sun_norm3)

    if include_moon:
        r_moon = get_moon_position(jd)
        r_moon_sat = r_sat - r_moon
        r_moon3 = np.linalg.norm(r_moon_sat)**3
        r_moon_norm3 = np.linalg.norm(r_moon)**3
        a += MU_MOON * (r_moon_sat / r_moon3 - r_moon / r_moon_norm3)

    return a
