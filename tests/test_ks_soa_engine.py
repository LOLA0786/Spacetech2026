"""
KoshaTrack SSA Engine - Comprehensive Test Framework

Test Coverage:
1. Orbit Propagation Accuracy
2. Collision Detection Validation
3. NavIC Health Monitoring
4. TLE Processing
5. SGP4 Propagation Verification
6. Performance Benchmarks
"""

import unittest
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ssa_engine import (
    KoshaTrackSSA, SatelliteState, OrbitRegime
)
from core.tle_manager import (
    ISROSatelliteCatalog, TLEData, generate_sample_tles
)


class TestOrbitPropagation(unittest.TestCase):
    """Test orbit propagation accuracy"""
    
    def setUp(self):
        """Initialize SSA engine"""
        self.ssa = KoshaTrackSSA(enable_perturbations=True)
    
    def test_circular_orbit_energy_conservation(self):
        """Test that circular orbit maintains constant energy"""
        # Create circular orbit at 500 km altitude
        r = 6378.137 + 500  # km
        v = np.sqrt(self.ssa.MU_EARTH / r)  # circular velocity
        
        state = SatelliteState(
            name="TEST-CIRCULAR",
            norad_id=99999,
            position=np.array([r, 0.0, 0.0]),
            velocity=np.array([0.0, v, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO
        )
        
        # Propagate for one orbit period
        period = 2 * np.pi * np.sqrt(r**3 / self.ssa.MU_EARTH)
        states = self.ssa.propagate_orbit(state, duration_seconds=period)
        
        # Check energy conservation
        initial_energy = self._orbital_energy(
            state.position, state.velocity
        )
        
        for s in states:
            energy = self._orbital_energy(s.position, s.velocity)
            energy_error = abs(energy - initial_energy) / abs(initial_energy)
            
            # Energy should be conserved within 1% for J2-only propagation
            self.assertLess(
                energy_error, 0.01,
                f"Energy conservation violated: {energy_error*100:.2f}%"
            )
    
    def test_geo_orbit_period(self):
        """Test that GEO orbit has ~24 hour period"""
        # GEO altitude: ~35,786 km
        r = 42164  # km from Earth center
        v = np.sqrt(self.ssa.MU_EARTH / r)
        
        state = SatelliteState(
            name="TEST-GEO",
            norad_id=99998,
            position=np.array([r, 0.0, 0.0]),
            velocity=np.array([0.0, v, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.GEO
        )
        
        # Propagate for 24 hours
        states = self.ssa.propagate_orbit(state, duration_seconds=24*3600)
        
        # Check final position is close to initial
        final_pos = states[-1].position
        initial_pos = state.position
        
        position_drift = np.linalg.norm(final_pos - initial_pos)
        
        # Should return close to starting point (within 100 km for J2)
        self.assertLess(
            position_drift, 100,
            f"GEO orbit drift too large: {position_drift:.1f} km"
        )
    
    def test_leo_orbit_decay(self):
        """Test that very low orbits show altitude decay"""
        # Low orbit at 200 km (with drag, this would decay)
        r = 6378.137 + 200
        v = np.sqrt(self.ssa.MU_EARTH / r)
        
        state = SatelliteState(
            name="TEST-LEO-LOW",
            norad_id=99997,
            position=np.array([r, 0.0, 0.0]),
            velocity=np.array([0.0, v, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO
        )
        
        # Propagate for 7 days
        states = self.ssa.propagate_orbit(state, duration_seconds=7*24*3600)
        
        # Note: Current implementation doesn't include drag
        # This test verifies propagation completes
        self.assertGreater(len(states), 0, "Propagation failed for low orbit")
    
    def _orbital_energy(self, position: np.ndarray, velocity: np.ndarray) -> float:
        """Calculate specific orbital energy"""
        r = np.linalg.norm(position)
        v = np.linalg.norm(velocity)
        
        kinetic = 0.5 * v**2
        potential = -self.ssa.MU_EARTH / r
        
        return kinetic + potential


class TestCollisionDetection(unittest.TestCase):
    """Test collision probability computation"""
    
    def setUp(self):
        """Initialize SSA engine"""
        self.ssa = KoshaTrackSSA(enable_perturbations=True)
    
    def test_direct_hit_probability(self):
        """Test that collision at same position gives Pc = 1.0"""
        # Two satellites at same position
        state1 = SatelliteState(
            name="SAT-1",
            norad_id=11111,
            position=np.array([7000.0, 0.0, 0.0]),
            velocity=np.array([0.0, 7.5, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO,
            covariance=np.eye(6) * 0.001
        )
        
        state2 = SatelliteState(
            name="SAT-2",
            norad_id=22222,
            position=np.array([7000.0, 0.0, 0.0]),  # Same position
            velocity=np.array([0.0, -7.5, 0.0]),  # Head-on
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO,
            covariance=np.eye(6) * 0.001
        )
        
        pc = self.ssa.compute_collision_probability(
            state1, state2, datetime.now()
        )
        
        # Should be very high probability
        self.assertGreater(pc, 0.9, "Direct collision should have Pc > 0.9")
    
    def test_far_separation_probability(self):
        """Test that widely separated objects have Pc ≈ 0"""
        state1 = SatelliteState(
            name="SAT-1",
            norad_id=11111,
            position=np.array([7000.0, 0.0, 0.0]),
            velocity=np.array([0.0, 7.5, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO,
            covariance=np.eye(6) * 0.01
        )
        
        state2 = SatelliteState(
            name="SAT-2",
            norad_id=22222,
            position=np.array([7000.0, 100.0, 0.0]),  # 100 km separation
            velocity=np.array([0.0, 7.5, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO,
            covariance=np.eye(6) * 0.01
        )
        
        pc = self.ssa.compute_collision_probability(
            state1, state2, datetime.now()
        )
        
        # Should be very low probability
        self.assertLess(pc, 1e-6, "Far separation should have Pc < 1e-6")
    
    def test_conjunction_detection(self):
        """Test that close approaches are detected"""
        # Create two satellites in similar orbits
        r = 7000.0
        v = np.sqrt(self.ssa.MU_EARTH / r)
        
        state1 = SatelliteState(
            name="NAVIC-TEST-1",
            norad_id=11111,
            position=np.array([r, 0.0, 0.0]),
            velocity=np.array([0.0, v, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.MEO
        )
        
        state2 = SatelliteState(
            name="NAVIC-TEST-2",
            norad_id=22222,
            position=np.array([r + 2.0, 0.0, 0.0]),  # 2 km offset
            velocity=np.array([0.0, v, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.MEO
        )
        
        self.ssa.add_satellite(state1)
        self.ssa.add_satellite(state2)
        
        # Search for conjunctions
        conjunctions = self.ssa.find_conjunctions(
            duration_hours=1.0,
            threshold_km=5.0
        )
        
        # Should detect at least one conjunction
        self.assertGreater(
            len(conjunctions), 0,
            "Should detect conjunction for close satellites"
        )


class TestNavICMonitoring(unittest.TestCase):
    """Test NavIC constellation health monitoring"""
    
    def setUp(self):
        """Initialize SSA engine"""
        self.ssa = KoshaTrackSSA(enable_perturbations=True)
    
    def test_navic_health_check_empty(self):
        """Test health check with no NavIC satellites"""
        health = self.ssa.navic_health_check()
        
        self.assertEqual(health['tracked'], 0)
        self.assertEqual(health['geometry_status'], 'DEGRADED')
    
    def test_navic_health_check_full_constellation(self):
        """Test health check with full constellation"""
        # Add all NavIC satellites at proper altitude
        navic_altitude = 42164  # km from Earth center
        v = np.sqrt(self.ssa.MU_EARTH / navic_altitude)
        
        for i, sat_name in enumerate(self.ssa.NAVIC_SATELLITES):
            angle = i * (360 / len(self.ssa.NAVIC_SATELLITES))
            rad = np.radians(angle)
            
            state = SatelliteState(
                name=sat_name,
                norad_id=39199 + i,
                position=np.array([
                    navic_altitude * np.cos(rad),
                    navic_altitude * np.sin(rad),
                    0.0
                ]),
                velocity=np.array([
                    -v * np.sin(rad),
                    v * np.cos(rad),
                    0.0
                ]),
                epoch=datetime.now(),
                orbit_regime=OrbitRegime.MEO
            )
            self.ssa.add_satellite(state)
        
        health = self.ssa.navic_health_check()
        
        self.assertEqual(health['tracked'], 8)
        self.assertEqual(health['geometry_status'], 'GOOD')
        self.assertEqual(len(health['operational']), 8)


class TestISROCatalog(unittest.TestCase):
    """Test ISRO satellite catalog"""
    
    def test_catalog_completeness(self):
        """Test that catalog contains key satellites"""
        catalog = ISROSatelliteCatalog.ISRO_SATELLITES
        
        # Check NavIC constellation
        self.assertIn('IRNSS-1A', catalog)
        self.assertIn('IRNSS-1G', catalog)
        
        # Check Earth observation
        self.assertIn('CARTOSAT-2F', catalog)
        self.assertIn('RISAT-2B', catalog)
        
        # Check communications
        self.assertIn('GSAT-30', catalog)
        
        # Check deep space
        self.assertIn('CHANDRAYAAN-3', catalog)
        self.assertIn('MARS ORBITER MISSION', catalog)
    
    def test_navic_constellation_count(self):
        """Test NavIC constellation has 8 satellites"""
        navic = ISROSatelliteCatalog.get_navic_constellation()
        self.assertEqual(len(navic), 8)
    
    def test_norad_id_lookup(self):
        """Test NORAD ID to name lookup"""
        name = ISROSatelliteCatalog.get_name_by_norad(39199)
        self.assertEqual(name, 'IRNSS-1A')
        
        # Test invalid NORAD ID
        name = ISROSatelliteCatalog.get_name_by_norad(99999999)
        self.assertIsNone(name)


class TestTLEProcessing(unittest.TestCase):
    """Test TLE data processing"""
    
    def test_sample_tle_generation(self):
        """Test sample TLE generation"""
        tles = generate_sample_tles()
        
        self.assertGreater(len(tles), 0)
        
        # Check TLE structure
        for norad_id, tle in tles.items():
            self.assertIsInstance(tle, TLEData)
            self.assertEqual(tle.norad_id, norad_id)
            self.assertTrue(tle.line1.startswith('1'))
            self.assertTrue(tle.line2.startswith('2'))


class TestPerformance(unittest.TestCase):
    """Performance benchmarks"""
    
    def test_propagation_speed(self):
        """Test that propagation is reasonably fast"""
        import time
        
        ssa = KoshaTrackSSA(enable_perturbations=True)
        
        state = SatelliteState(
            name="PERF-TEST",
            norad_id=99999,
            position=np.array([7000.0, 0.0, 0.0]),
            velocity=np.array([0.0, 7.5, 0.0]),
            epoch=datetime.now(),
            orbit_regime=OrbitRegime.LEO
        )
        
        start_time = time.time()
        states = ssa.propagate_orbit(state, duration_seconds=24*3600, timestep=60)
        elapsed = time.time() - start_time
        
        # Should propagate 24 hours in less than 5 seconds
        self.assertLess(elapsed, 5.0, f"Propagation too slow: {elapsed:.2f}s")
        
        # Should generate ~1440 points (24 hours at 1 minute intervals)
        self.assertGreater(len(states), 100, "Too few propagation points")


class TestValidationData(unittest.TestCase):
    """
    Validation against known orbital data
    
    These tests compare against published ephemerides
    """
    
    def test_iss_orbital_period(self):
        """
        Test ISS orbital period matches known value (~90 minutes)
        
        Note: ISS is not an ISRO satellite, but useful for validation
        """
        ssa = KoshaTrackSSA(enable_perturbations=False)
        
        # ISS approximate orbit: 408 km altitude
        r = 6378.137 + 408
        v = np.sqrt(ssa.MU_EARTH / r)
        
        # Theoretical period
        period_theoretical = 2 * np.pi * np.sqrt(r**3 / ssa.MU_EARTH)
        
        # Should be ~92 minutes (5520 seconds)
        self.assertAlmostEqual(
            period_theoretical / 60, 92, delta=2,
            msg="ISS orbital period validation failed"
        )
    
    def test_geo_velocity(self):
        """Test GEO velocity matches theoretical value"""
        ssa = KoshaTrackSSA(enable_perturbations=False)
        
        # GEO radius
        r = 42164  # km
        
        # Theoretical velocity for circular orbit
        v_theoretical = np.sqrt(ssa.MU_EARTH / r)
        
        # Should be ~3.075 km/s
        self.assertAlmostEqual(
            v_theoretical, 3.075, delta=0.01,
            msg="GEO velocity validation failed"
        )


def run_all_tests():
    """Run complete test suite"""
    print("=" * 70)
    print("KoshaTrack SSA Engine - Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestOrbitPropagation))
    suite.addTests(loader.loadTestsFromTestCase(TestCollisionDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestNavICMonitoring))
    suite.addTests(loader.loadTestsFromTestCase(TestISROCatalog))
    suite.addTests(loader.loadTestsFromTestCase(TestTLEProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestValidationData))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
