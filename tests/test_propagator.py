import pytest
import numpy as np
from datetime import datetime

from src.ssa.propagator import propagate_tle, get_iss_position_now, validate_orbital_elements
from sgp4.api import Satrec

# Known good ISS TLE (approx)
GOOD_LINE1 = "1 25544U 98067A   26014.62222222  .00001234  00000-0  12345-4 0  9996"
GOOD_LINE2 = "2 25544  51.6433  123.4567 0001234  90.0000 270.0000 15.48901234 56789"

# Bad eccentricity >1
BAD_LINE1 = "1 99999U 99999A   00001.00000000  .00000000  00000-0  99999-4 0  0001"
BAD_LINE2 = "2 99999  45.0000   0.0000 1000000   0.0000   0.0000  1.00000000 00008"

def test_validate_good():
    sat = Satrec.twoline2rv(GOOD_LINE1, GOOD_LINE2)
    validate_orbital_elements(sat)  # Should not raise

def test_validate_bad_ecc():
    sat = Satrec.twoline2rv(BAD_LINE1, BAD_LINE2)
    with pytest.raises(ValueError, match="Invalid eccentricity"):
        validate_orbital_elements(sat)

def test_propagate_returns_structure():
    result = propagate_tle(GOOD_LINE1, GOOD_LINE2)
    assert "timestamp_utc" in result
    assert "position_eci_km" in result
    assert len(result["position_eci_km"]) == 3
    assert "velocity_eci_km_s" in result

def test_propagate_reasonable_leo():
    result = propagate_tle(GOOD_LINE1, GOOD_LINE2)
    pos_mag = np.linalg.norm(result["position_eci_km"])
    assert 6000 < pos_mag < 9000  # Rough Earth radius + LEO altitude

def test_iss_live_fetch():
    result = get_iss_position_now()
    assert "iss_zarya_fresh_celestrak" in result["source"]
    assert len(result["position_eci_km"]) == 3
