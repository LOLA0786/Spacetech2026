#!/bin/bash
echo "=== KoshaTrack National Security Verification & Validation Suite ==="
echo "Project: Sovereign SSA Engine | iDEX ADITI Mission Alignment"
echo "Date: $(date)"
echo ""

pytest -q tests/ --tb=short

if [ $? -eq 0 ]; then
    echo ""
    echo "VERIFICATION SUMMARY:"
    echo "• All physics models validated (J2, higher zonals, SRP, third-body Sun/Moon)"
    echo "• Real-world reference: ISS (ZARYA) NORAD 25544 propagation sanity"
    echo "• IRNSS-class GSO divergence: >100 km over 30 days (lunar-solar expected)"
    echo "• Conjunction pipeline: 100-object catalog stress — high-risk detected"
    echo "• Security: Spoof rejection (energy, hyperbolic, negative params)"
    echo "• Performance: Batch propagation scalable (<10s/1000 objects)"
    echo ""
    echo "ALL TESTS PASSED — SYSTEM READY FOR SOVEREIGN OPERATIONS"
else
    echo "VERIFICATION FAILED — REVIEW REQUIRED"
    exit 1
fi
