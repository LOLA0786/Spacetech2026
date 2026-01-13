from datetime import datetime
from typing import Dict
import logging

from sgp4.api import Satrec
from sgp4.conveniences import sat_epoch_datetime

logger = logging.getLogger(__name__)


class OrbitPropagator:
    def __init__(self):
        self.satellites: Dict[str, Satrec] = {}

    def load_tle(self, name: str, line1: str, line2: str) -> bool:
        try:
            sat = Satrec.twoline2rv(line1, line2)
            self.satellites[name] = sat
            return True
        except Exception as e:
            logger.error(f"Failed to load TLE for {name}: {e}")
            return False

    def propagate(self, sat_name: str, time: datetime) -> Dict:
        if sat_name not in self.satellites:
            raise ValueError(f"Satellite not found: {sat_name}")

        sat = self.satellites[sat_name]

        # Convert datetime to Julian
        jd, fr = self._datetime_to_jday(time)

        e, r, v = sat.sgp4(jd, fr)
        if e != 0:
            raise ValueError(f"Propagation error code: {e}")

        return {
            "satellite": sat_name,
            "timestamp": time.isoformat(),
            "position": {"x": float(r[0]), "y": float(r[1]), "z": float(r[2])},  # km TEME
            "velocity": {"vx": float(v[0]), "vy": float(v[1]), "vz": float(v[2])},  # km/s TEME
        }

    def calculate_collision_probability(self, sat1: str, sat2: str, time_window_days: int = 7) -> Dict:
        # MVP placeholder – real implementation needs conjunction assessment + covariance
        if sat1 not in self.satellites or sat2 not in self.satellites:
            raise ValueError("Satellite not found")

        return {
            "sat1": sat1,
            "sat2": sat2,
            "time_window_days": time_window_days,
            "probability": 0.000001,
            "note": "MVP placeholder. Implement real conjunction analysis later.",
        }

    def _datetime_to_jday(self, dt: datetime):
        # Julian Day conversion
        # Source-safe simple implementation
        year = dt.year
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second + dt.microsecond / 1e6

        if month <= 2:
            year -= 1
            month += 12

        A = year // 100
        B = 2 - A + (A // 4)

        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        fr = (hour + (minute + second / 60.0) / 60.0) / 24.0
        return jd, fr
