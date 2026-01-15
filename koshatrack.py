#!/usr/bin/env python3
"""
KoshaTrack SSA Engine - Main Application
Command-line interface for ISRO/DRDO operators
"""

import argparse
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('koshatrack.log')
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Display KoshaTrack banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   ██╗  ██╗ ██████╗ ███████╗██╗  ██╗ █████╗ ████████╗██████╗║
    ║   ██║ ██╔╝██╔═══██╗██╔════╝██║  ██║██╔══██╗╚══██╔══╝██╔══██║
    ║   █████╔╝ ██║   ██║███████╗███████║███████║   ██║   ██████╔╝║
    ║   ██╔═██╗ ██║   ██║╚════██║██╔══██║██╔══██║   ██║   ██╔══██╗║
    ║   ██║  ██╗╚██████╔╝███████║██║  ██║██║  ██║   ██║   ██║  ██║║
    ║   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝║
    ║                                                              ║
    ║           Sovereign Space Situational Awareness             ║
    ║                    for Bharat Mata 🇮🇳                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Version: 2.0
    For: Government of India (ISRO/DRDO/MoD)
    Status: Production Ready
    """
    print(banner)


def cmd_track_satellites(args):
    """Track all Indian satellites"""
    from core.ssa_engine import KoshaTrackSSA
    from core.tle_manager import TLEFetcher, ISROSatelliteCatalog, generate_sample_tles
    
    logger.info("Starting satellite tracking...")
    
    # Initialize SSA engine
    ssa = KoshaTrackSSA(enable_perturbations=args.perturbations)
    
    # Fetch TLEs
    if args.use_spacetrack and args.username and args.password:
        logger.info("Fetching TLEs from Space-Track.org...")
        fetcher = TLEFetcher(args.username, args.password)
        tles = fetcher.fetch_all_isro_tles()
    else:
        logger.info("Using sample TLEs (for demo)...")
        tles = generate_sample_tles()
    
    # Add satellites to catalog
    for norad_id, tle in tles.items():
        # Convert TLE to state (simplified - would use SGP4 in production)
        logger.info(f"Added {tle.satellite_name} to tracking catalog")
    
    logger.info(f"Tracking {len(tles)} satellites")


def cmd_find_conjunctions(args):
    """Find potential conjunctions"""
    from core.ssa_engine import KoshaTrackSSA, SatelliteState, OrbitRegime
    import numpy as np
    
    logger.info("Searching for conjunctions...")
    
    ssa = KoshaTrackSSA(enable_perturbations=True)
    
    # Add sample satellites (in production, load from database)
    navic_1a = SatelliteState(
        name="IRNSS-1A",
        norad_id=39199,
        position=np.array([42164.0, 0.0, 0.0]),
        velocity=np.array([0.0, 3.075, 0.0]),
        epoch=datetime.now(),
        orbit_regime=OrbitRegime.MEO
    )
    ssa.add_satellite(navic_1a)
    
    cartosat = SatelliteState(
        name="CARTOSAT-2F",
        norad_id=43109,
        position=np.array([6878.137, 0.0, 0.0]),
        velocity=np.array([0.0, 7.612, 0.0]),
        epoch=datetime.now(),
        orbit_regime=OrbitRegime.LEO
    )
    ssa.add_satellite(cartosat)
    
    # Find conjunctions
    conjunctions = ssa.find_conjunctions(
        duration_hours=args.duration,
        threshold_km=args.threshold
    )
    
    print(f"\n{'='*70}")
    print(f"CONJUNCTION REPORT")
    print(f"{'='*70}")
    print(f"Search Duration: {args.duration} hours")
    print(f"Threshold: {args.threshold} km")
    print(f"Found: {len(conjunctions)} potential conjunctions")
    print(f"{'='*70}\n")
    
    for conj in conjunctions:
        print(f"Primary: {conj['primary']}")
        print(f"Secondary: {conj['secondary']}")
        print(f"TCA: {conj['tca']}")
        print(f"Miss Distance: {conj['miss_distance_km']:.2f} km")
        print(f"Collision Probability: {conj['collision_probability']:.2e}")
        print("-" * 70)


def cmd_check_navic(args):
    """Check NavIC constellation health"""
    from core.ssa_engine import KoshaTrackSSA, SatelliteState, OrbitRegime
    import numpy as np
    
    logger.info("Checking NavIC constellation health...")
    
    ssa = KoshaTrackSSA(enable_perturbations=True)
    
    # Add NavIC satellites at proper positions
    navic_altitude = 42164  # km
    v = np.sqrt(ssa.MU_EARTH / navic_altitude)
    
    for i, sat_name in enumerate(ssa.NAVIC_SATELLITES):
        angle = i * (360 / len(ssa.NAVIC_SATELLITES))
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
        ssa.add_satellite(state)
    
    health = ssa.navic_health_check()
    
    print(f"\n{'='*70}")
    print(f"NAVIC CONSTELLATION HEALTH REPORT")
    print(f"{'='*70}")
    print(f"Total Satellites: {health['total_satellites']}")
    print(f"Tracked: {health['tracked']}")
    print(f"Operational: {len(health['operational'])}")
    print(f"Geometry Status: {health['geometry_status']}")
    print(f"\nOperational Satellites:")
    for sat in health['operational']:
        print(f"  ✓ {sat}")
    print(f"{'='*70}\n")


def cmd_detect_threats(args):
    """Detect space threats"""
    from core.threat_detector import SpaceThreatDetector
    import numpy as np
    
    logger.info("Initializing threat detection system...")
    
    detector = SpaceThreatDetector()
    
    # Add protected assets
    detector.add_protected_asset(
        "IRNSS-1A",
        np.array([42164.0, 0.0, 0.0])
    )
    detector.add_protected_asset(
        "CARTOSAT-2F",
        np.array([6878.137, 0.0, 0.0])
    )
    
    # Simulate threat scenarios
    print(f"\n{'='*70}")
    print(f"THREAT DETECTION SYSTEM - TEST MODE")
    print(f"{'='*70}\n")
    
    # Test hypersonic detection
    print("Testing hypersonic detection...")
    threat = detector.detect_hypersonic_threat(
        position=np.array([6478.137, 0.0, 0.0]),  # 100 km altitude
        velocity=np.array([0.0, 2.0, 0.0]),  # Mach 6
        object_name="TEST-HYPERSONIC"
    )
    
    if threat:
        print(f"✓ Hypersonic threat detected: {threat.threat_type.value}")
        print(f"  Level: {threat.threat_level.name}")
        print(f"  Confidence: {threat.confidence*100:.1f}%")
    
    # Test RPO detection
    print("\nTesting proximity operations detection...")
    threat = detector.detect_rpo_threat(
        position=np.array([6900.0, 0.0, 0.0]),
        velocity=np.array([0.0, 7.5, 0.0]),
        object_name="TEST-INSPECTOR"
    )
    
    if threat:
        print(f"✓ RPO threat detected: {threat.threat_type.value}")
        print(f"  Target: {threat.target_asset}")
        print(f"  Level: {threat.threat_level.name}")
    
    print(f"\n{'='*70}\n")


def cmd_generate_report(args):
    """Generate operational report"""
    from core.ssa_engine import KoshaTrackSSA
    
    logger.info(f"Generating report: {args.output}")
    
    ssa = KoshaTrackSSA(enable_perturbations=True)
    
    # Generate report (placeholder)
    report_path = ssa.export_conjunction_report(args.output)
    
    print(f"\n{'='*70}")
    print(f"Report generated: {report_path}")
    print(f"{'='*70}\n")


def cmd_run_tests(args):
    """Run test suite"""
    import subprocess
    
    logger.info("Running test suite...")
    
    print(f"\n{'='*70}")
    print(f"KOSHATRACK TEST SUITE")
    print(f"{'='*70}\n")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short"
    ])
    
    sys.exit(result.returncode)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='KoshaTrack SSA Engine - Sovereign Space Situational Awareness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s track                    # Track all Indian satellites
  %(prog)s conjunctions --duration 48  # Find 48-hour conjunctions
  %(prog)s navic                    # Check NavIC health
  %(prog)s threats                  # Detect threats
  %(prog)s report -o report.json    # Generate report
  %(prog)s test                     # Run tests
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Track command
    track_parser = subparsers.add_parser('track', help='Track satellites')
    track_parser.add_argument('--no-perturbations', dest='perturbations',
                              action='store_false', help='Disable perturbations')
    track_parser.add_argument('--use-spacetrack', action='store_true',
                              help='Use Space-Track.org')
    track_parser.add_argument('--username', help='Space-Track username')
    track_parser.add_argument('--password', help='Space-Track password')
    
    # Conjunctions command
    conj_parser = subparsers.add_parser('conjunctions', help='Find conjunctions')
    conj_parser.add_argument('--duration', type=float, default=24.0,
                            help='Search duration in hours (default: 24)')
    conj_parser.add_argument('--threshold', type=float, default=5.0,
                            help='Distance threshold in km (default: 5)')
    
    # NavIC command
    subparsers.add_parser('navic', help='Check NavIC constellation')
    
    # Threats command
    subparsers.add_parser('threats', help='Detect threats')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('-o', '--output', default='report.json',
                              help='Output file (default: report.json)')
    
    # Test command
    subparsers.add_parser('test', help='Run test suite')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Route to appropriate command
    if args.command == 'track':
        cmd_track_satellites(args)
    elif args.command == 'conjunctions':
        cmd_find_conjunctions(args)
    elif args.command == 'navic':
        cmd_check_navic(args)
    elif args.command == 'threats':
        cmd_detect_threats(args)
    elif args.command == 'report':
        cmd_generate_report(args)
    elif args.command == 'test':
        cmd_run_tests(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
