"""
Space-Track.org API Client for TLE Data
"""
import requests
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
import os

class SpaceTrackClient:
    """
    Client for Space-Track.org API
    Docs: https://www.space-track.org/documentation
    """
    
    BASE_URL = "https://www.space-track.org"
    
    def __init__(self, username: str = None, password: str = None):
        """
        Initialize Space-Track client
        
        Args:
            username: Space-Track username (or set SPACETRACK_USERNAME env var)
            password: Space-Track password (or set SPACETRACK_PASSWORD env var)
        """
        self.username = username or os.getenv('SPACETRACK_USERNAME')
        self.password = password or os.getenv('SPACETRACK_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError(
                "Space-Track credentials required. "
                "Set SPACETRACK_USERNAME and SPACETRACK_PASSWORD env vars "
                "or pass to constructor."
            )
        
        self.session = requests.Session()
        self._login()
    
    def _login(self):
        """Authenticate with Space-Track"""
        login_url = f"{self.BASE_URL}/ajaxauth/login"
        
        data = {
            'identity': self.username,
            'password': self.password
        }
        
        try:
            resp = self.session.post(login_url, data=data)
            resp.raise_for_status()
            print("✓ Authenticated with Space-Track.org")
        except Exception as e:
            raise ConnectionError(f"Space-Track login failed: {e}")
    
    def get_tle_latest(self, norad_ids: List[int] = None, 
                       limit: int = 1000) -> List[Dict]:
        """
        Get latest TLEs for specified satellites
        
        Args:
            norad_ids: List of NORAD catalog IDs (None = all active)
            limit: Max number of results
            
        Returns:
            List of TLE dictionaries
        """
        query = f"{self.BASE_URL}/basicspacedata/query/class/tle_latest/ORDINAL/1"
        
        if norad_ids:
            norad_filter = ','.join(str(n) for n in norad_ids)
            query += f"/NORAD_CAT_ID/{norad_filter}"
        
        query += f"/orderby/NORAD_CAT_ID/limit/{limit}/format/json"
        
        try:
            resp = self.session.get(query)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"✓ Retrieved {len(data)} TLEs from Space-Track")
            return data
            
        except Exception as e:
            print(f"✗ Error fetching TLEs: {e}")
            return []
    
    def get_tle_history(self, norad_id: int, days: int = 30) -> List[Dict]:
        """
        Get TLE history for a satellite
        
        Args:
            norad_id: NORAD catalog ID
            days: Number of days of history
            
        Returns:
            List of historical TLEs
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = (
            f"{self.BASE_URL}/basicspacedata/query/class/tle/"
            f"NORAD_CAT_ID/{norad_id}/"
            f"EPOCH/{start_date.strftime('%Y-%m-%d')}--{end_date.strftime('%Y-%m-%d')}/"
            f"orderby/EPOCH asc/format/json"
        )
        
        try:
            resp = self.session.get(query)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"✗ Error fetching TLE history: {e}")
            return []
    
    def get_cdm_messages(self, days: int = 7) -> List[Dict]:
        """
        Get Conjunction Data Messages (CDMs) from Space-Track
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of CDM dictionaries
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = (
            f"{self.BASE_URL}/basicspacedata/query/class/cdm_public/"
            f"CREATION_DATE/{start_date.strftime('%Y-%m-%d')}--{end_date.strftime('%Y-%m-%d')}/"
            f"orderby/CREATION_DATE desc/format/json"
        )
        
        try:
            resp = self.session.get(query)
            resp.raise_for_status()
            data = resp.json()
            
            print(f"✓ Retrieved {len(data)} CDMs from Space-Track")
            return data
            
        except Exception as e:
            print(f"✗ Error fetching CDMs: {e}")
            return []
    
    def close(self):
        """Close session"""
        self.session.close()

# Example usage
if __name__ == "__main__":
    # Create client (requires Space-Track account)
    # Sign up free at https://www.space-track.org/auth/createAccount
    
    try:
        client = SpaceTrackClient()
        
        # Get latest TLE for ISS (NORAD ID 25544)
        tle_data = client.get_tle_latest(norad_ids=[25544])
        
        if tle_data:
            tle = tle_data[0]
            print(f"\nISS TLE:")
            print(f"Name: {tle.get('OBJECT_NAME')}")
            print(f"Line 1: {tle.get('TLE_LINE1')}")
            print(f"Line 2: {tle.get('TLE_LINE2')}")
            print(f"Epoch: {tle.get('EPOCH')}")
        
        client.close()
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("\nTo use Space-Track API:")
        print("1. Sign up at https://www.space-track.org/auth/createAccount")
        print("2. Set environment variables:")
        print("   export SPACETRACK_USERNAME='your_username'")
        print("   export SPACETRACK_PASSWORD='your_password'")
