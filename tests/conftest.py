"""
Pytest configuration and fixtures
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest

@pytest.fixture
def sample_tle():
    """Sample TLE for ISS"""
    return {
        'name': 'ISS (ZARYA)',
        'line1': '1 25544U 98067A   24014.50000000  .00012456  00000-0  22132-3 0  9998',
        'line2': '2 25544  51.6416 286.4027 0001137  61.8281  83.3421 15.50030372434161'
    }

@pytest.fixture
def sample_observation():
    """Sample orbital observation (position in km)"""
    return [7000.0, 0.0, 0.0]
