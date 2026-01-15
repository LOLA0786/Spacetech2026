"""
TLE Data Management for KoshaTrack SSA Engine

Features:
1. Fetch TLEs from Space-Track.org (US Space Command)
2. Parse ISRO satellite catalog
3. Maintain sovereign database of Indian space assets
4. SGP4 propagation from TLE data
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
import numpy as np

# SGP4 propagator - industry standard
try:
    from sgp4.api import Satrec, jday
    from sgp4 import exporter
    SGP4_AVAILABLE = True
except ImportError:
    SGP4_AVAILABLE = False
    logging.warning("SGP4 not available. Install: pip install sgp4")

logger = logging.getLogger(__name__)


@dataclass
class TLEData:
    """Two-Line Element set"""
    satellite_name: str
    norad_id: int
    line1: str
    line2: str
    epoch: datetime
    source: str = "UNKNOWN"
    
    def __str__(self):
        return f"{self.satellite_name}\n{self.line1}\n{self.line2}"


class ISROSatelliteCatalog:
    """
    Comprehensive catalog of Indian space assets
    
    Sources:
    - ISRO official launches
    - Space-Track.org
    - Local sovereign database
    """
    
    # Indian satellite catalog (subset - to be expanded)
    ISRO_SATELLITES = {
        # NavIC/IRNSS Constellation
        'IRNSS-1A': 39199,
        'IRNSS-1B': 39635,
        'IRNSS-1C': 40269,
        'IRNSS-1D': 40547,
        'IRNSS-1E': 41384,
        'IRNSS-1F': 41469,
        'IRNSS-1G': 41920,
        'IRNSS-1I': 43286,
        
        # INSAT/GSAT Series (GEO Communications)
        'INSAT-3DR': 41791,
        'GSAT-15': 40948,
        'GSAT-16': 40332,
        'GSAT-17': 42797,
        'GSAT-18': 41792,
        'GSAT-19': 42662,
        'GSAT-29': 43662,
        'GSAT-30': 45269,
        'GSAT-31': 43991,
        
        # Earth Observation (LEO)
        'CARTOSAT-2': 30794,
        'CARTOSAT-2A': 32783,
        'CARTOSAT-2B': 36795,
        'CARTOSAT-2C': 41599,
        'CARTOSAT-2D': 41948,
        'CARTOSAT-2E': 42063,
        'CARTOSAT-2F': 43109,
        'CARTOSAT-3': 44804,
        
        # RISAT (Radar Imaging)
        'RISAT-1': 38248,
        'RISAT-2': 35493,
        'RISAT-2B': 44227,
        
        # Resourcesat/IRS Series
        'RESOURCESAT-2': 37387,
        'RESOURCESAT-2A': 42707,
        
        # Oceansat
        'OCEANSAT-2': 35931,
        'OCEANSAT-3': 51576,
        
        # Chandrayaan (Lunar)
        'CHANDRAYAAN-2': 44441,
        'CHANDRAYAAN-3': 57320,
        
        # Mars Orbiter Mission
        'MARS ORBITER MISSION': 39370,
        
        # Astrosat
        'ASTROSAT': 40930,
        
        # Recent Launches
        'EMISAT': 44275,
        'MICROSAT-R': 43947,
    }
    
    @classmethod
    def get_all_norad_ids(cls) -> List[int]:
        """Get all NORAD IDs for ISRO satellites"""
        return list(cls.ISRO_SATELLITES.values())
    
    @classmethod
    def get_name_by_norad(cls, norad_id: int) -> Optional[str]:
        """Get satellite name from NORAD ID"""
        for name, nid in cls.ISRO_SATELLITES.items():
            if nid == norad_id:
                return name
        return None
    
    @classmethod
    def get_navic_constellation(cls) -> Dict[str, int]:
        """Get NavIC constellation satellites"""
        return {k: v for k, v in cls.ISRO_SATELLITES.items() if 'IRNSS' in k}
    
    @classmethod
    def get_leo_satellites(cls) -> Dict[str, int]:
        """Get LEO satellites (Earth observation)"""
        leo_keywords = ['CARTOSAT', 'RISAT', 'RESOURCESAT', 'OCEANSAT', 'EMISAT']
        return {
            k: v for k, v in cls.ISRO_SATELLITES.items() 
            if any(kw in k for kw in leo_keywords)
        }
    
    @classmethod
    def get_geo_satellites(cls) -> Dict[str, int]:
        """Get GEO satellites (communications)"""
        geo_keywords = ['INSAT', 'GSAT']
        return {
            k: v for k, v in cls.ISRO_SATELLITES.items() 
            if any(kw in k for kw in geo_keywords)
        }


class TLEFetcher:
    """
    Fetch TLE data from Space-Track.org
    
    Requires Space-Track.org account (free for approved users)
    """
    
    SPACETRACK_URL = "https://www.space-track.org"
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize TLE fetcher
        
        Args:
            username: Space-Track.org username
            password: Space-Track.org password
        """
        self.username = username
        self.password = password
        self.session = None
        
    def login(self):
        """Login to Space-Track.org"""
        if not self.username or not self.password:
            logger.warning("No Space-Track credentials provided. Using cached TLEs only.")
            return False
        
        try:
            self.session = requests.Session()
            login_url = f"{self.SPACETRACK_URL}/ajaxauth/login"
            
            response = self.session.post(
                login_url,
                data={
                    'identity': self.username,
                    'password': self.password
                }
            )
            
            if response.status_code == 200:
                logger.info("Successfully logged in to Space-Track.org")
                return True
            else:
                logger.error(f"Space-Track login failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Space-Track login error: {e}")
            return False
    
    def fetch_tle_by_norad(self, norad_id: int) -> Optional[TLEData]:
        """
        Fetch latest TLE for a NORAD ID
        
        Args:
            norad_id: NORAD catalog number
            
        Returns:
            TLEData object or None
        """
        if not self.session:
            logger.warning("Not logged in. Attempting login...")
            if not self.login():
                return None
        
        try:
            # Query latest TLE
            query_url = (
                f"{self.SPACETRACK_URL}/basicspacedata/query/class/tle_latest/"
                f"NORAD_CAT_ID/{norad_id}/format/json"
            )
            
            response = self.session.get(query_url)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch TLE for NORAD {norad_id}")
                return None
            
            data = response.json()
            
            if not data:
                logger.warning(f"No TLE data found for NORAD {norad_id}")
                return None
            
            # Parse response
            tle_entry = data[0]
            
            return TLEData(
                satellite_name=tle_entry['OBJECT_NAME'],
                norad_id=int(tle_entry['NORAD_CAT_ID']),
                line1=tle_entry['TLE_LINE1'],
                line2=tle_entry['TLE_LINE2'],
                epoch=datetime.strptime(tle_entry['EPOCH'], '%Y-%m-%d %H:%M:%S'),
                source="Space-Track.org"
            )
            
        except Exception as e:
            logger.error(f"Error fetching TLE: {e}")
            return None
    
    def fetch_all_isro_tles(self) -> Dict[int, TLEData]:
        """
        Fetch TLEs for all ISRO satellites
        
        Returns:
            Dictionary mapping NORAD ID to TLEData
        """
        logger.info("Fetching TLEs for all ISRO satellites...")
        
        tles = {}
        norad_ids = ISROSatelliteCatalog.get_all_norad_ids()
        
        for norad_id in norad_ids:
            tle = self.fetch_tle_by_norad(norad_id)
            if tle:
                tles[norad_id] = tle
                logger.info(f"Fetched TLE for {tle.satellite_name}")
            else:
                logger.warning(f"Failed to fetch TLE for NORAD {norad_id}")
        
        logger.info(f"Successfully fetched {len(tles)} TLEs")
        return tles
    
    def save_tles_to_file(self, tles: Dict[int, TLEData], filepath: str):
        """Save TLEs to JSON file for offline use"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'source': 'Space-Track.org',
            'satellites': [
                {
                    'name': tle.satellite_name,
                    'norad_id': tle.norad_id,
                    'line1': tle.line1,
                    'line2': tle.line2,
                    'epoch': tle.epoch.isoformat()
                }
                for tle in tles.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"TLEs saved to {filepath}")
    
    def load_tles_from_file(self, filepath: str) -> Dict[int, TLEData]:
        """Load TLEs from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        tles = {}
        for sat in data['satellites']:
            tle = TLEData(
                satellite_name=sat['name'],
                norad_id=sat['norad_id'],
                line1=sat['line1'],
                line2=sat['line2'],
                epoch=datetime.fromisoformat(sat['epoch']),
                source=data['source']
            )
            tles[sat['norad_id']] = tle
        
        logger.info(f"Loaded {len(tles)} TLEs from {filepath}")
        return tles


class SGP4Propagator:
    """
    SGP4/SDP4 orbit propagator
    
    Industry standard for TLE propagation
    """
    
    def __init__(self, tle_data: TLEData):
        """
        Initialize SGP4 propagator with TLE
        
        Args:
            tle_data: TLE data object
        """
        if not SGP4_AVAILABLE:
            raise ImportError("SGP4 library not installed")
        
        self.tle = tle_data
        
        # Initialize SGP4 satellite object
        self.satellite = Satrec.twoline2rv(tle_data.line1, tle_data.line2)
        
        logger.info(f"SGP4 propagator initialized for {tle_data.satellite_name}")
    
    def propagate(self, target_time: datetime) -> Optional[Dict]:
        """
        Propagate orbit to target time
        
        Args:
            target_time: Target datetime
            
        Returns:
            Position and velocity in TEME frame (km, km/s)
        """
        # Convert datetime to Julian date
        jd, fr = jday(
            target_time.year,
            target_time.month,
            target_time.day,
            target_time.hour,
            target_time.minute,
            target_time.second + target_time.microsecond / 1e6
        )
        
        # Propagate
        error_code, position, velocity = self.satellite.sgp4(jd, fr)
        
        if error_code != 0:
            logger.error(f"SGP4 propagation error: {error_code}")
            return None
        
        return {
            'epoch': target_time,
            'position': np.array(position),  # km
            'velocity': np.array(velocity),  # km/s
            'frame': 'TEME'  # True Equator Mean Equinox
        }
    
    def propagate_multiple(
        self, 
        start_time: datetime,
        duration_hours: float,
        timestep_minutes: float = 10.0
    ) -> List[Dict]:
        """
        Propagate over time period
        
        Args:
            start_time: Start time
            duration_hours: Duration in hours
            timestep_minutes: Time step in minutes
            
        Returns:
            List of state vectors
        """
        states = []
        current_time = start_time
        end_time = start_time + timedelta(hours=duration_hours)
        
        while current_time <= end_time:
            state = self.propagate(current_time)
            if state:
                states.append(state)
            current_time += timedelta(minutes=timestep_minutes)
        
        logger.info(f"Generated {len(states)} ephemeris points")
        return states


def generate_sample_tles() -> Dict[int, TLEData]:
    """
    Generate sample TLEs for testing (when Space-Track unavailable)
    
    These are approximate TLEs for demonstration
    """
    sample_tles = {
        39199: TLEData(  # IRNSS-1A
            satellite_name="IRNSS-1A",
            norad_id=39199,
            line1="1 39199U 13034A   24015.50000000  .00000000  00000-0  00000+0 0  9999",
            line2="2 39199  29.0000  55.0000 0000100 000.0000 000.0000  1.00273791999999",
            epoch=datetime.now(),
            source="SAMPLE"
        ),
        43109: TLEData(  # CARTOSAT-2F
            satellite_name="CARTOSAT-2F",
            norad_id=43109,
            line1="1 43109U 18004A   24015.50000000  .00000100  00000-0  10000-3 0  9999",
            line2="2 43109  97.8000 100.0000 0001000 000.0000 000.0000 14.20000000999999",
            epoch=datetime.now(),
            source="SAMPLE"
        )
    }
    
    logger.info("Generated sample TLEs for testing")
    return sample_tles


if __name__ == "__main__":
    print("=" * 60)
    print("KoshaTrack TLE Data Management")
    print("=" * 60)
    
    # Display ISRO satellite catalog
    print("\n--- ISRO Satellite Catalog ---")
    print(f"Total satellites: {len(ISROSatelliteCatalog.ISRO_SATELLITES)}")
    print(f"NavIC constellation: {len(ISROSatelliteCatalog.get_navic_constellation())}")
    print(f"LEO satellites: {len(ISROSatelliteCatalog.get_leo_satellites())}")
    print(f"GEO satellites: {len(ISROSatelliteCatalog.get_geo_satellites())}")
    
    # Use sample TLEs for demo
    print("\n--- Generating Sample TLEs ---")
    tles = generate_sample_tles()
    
    # Test SGP4 propagation
    if SGP4_AVAILABLE:
        print("\n--- Testing SGP4 Propagation ---")
        for norad_id, tle in tles.items():
            print(f"\nPropagating {tle.satellite_name}...")
            propagator = SGP4Propagator(tle)
            
            # Propagate 24 hours
            states = propagator.propagate_multiple(
                start_time=datetime.now(),
                duration_hours=24,
                timestep_minutes=60
            )
            
            print(f"Generated {len(states)} state vectors")
            if states:
                print(f"First position: {states[0]['position']} km")
    else:
        print("\nSGP4 not available. Install with: pip install sgp4")
    
    print("\n" + "=" * 60)
