#!/bin/bash
# KoshaTrack SSA Engine - Verify3
# GSO/GEO Drift Validation (IRNSS / GSO third-body + zonals)

set -euo pipefail

echo "======================================================================"
echo "  KoshaTrack Verify3 - GSO/GEO Drift Validation"
echo "======================================================================"
echo ""

mkdir -p reports/vv

TS=$(date +"%Y%m%d_%H%M%S")
OUT="reports/vv/verify3_gso_irnss_${TS}.txt"

echo "[*] Running GSO/IRNSS drift comparison..."
echo "[*] Output: ${OUT}"
echo ""

python3 scripts/compare_gso_irnss.py | tee "${OUT}"

echo ""
echo "======================================================================"
echo "✅ VERIFY3 COMPLETE"
echo "Evidence saved to: ${OUT}"
echo "======================================================================"
