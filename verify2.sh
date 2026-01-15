#!/bin/bash
# KoshaTrack SSA Engine - Verify2
# Legacy vs Full Perturbations Evidence Run (ISS Case)

set -euo pipefail

echo "======================================================================"
echo "  KoshaTrack Verify2 - Legacy vs Full Perturbations (ISS Validation)"
echo "======================================================================"
echo ""

mkdir -p reports/vv

TS=$(date +"%Y%m%d_%H%M%S")
OUT="reports/vv/verify2_iss_comparison_${TS}.txt"

echo "[*] Running ISS propagation comparison script..."
echo "[*] Output: ${OUT}"
echo ""

# Run + tee output to file
python3 scripts/compare_legacy_vs_full_iss.py | tee "${OUT}"

echo ""
echo "======================================================================"
echo "✅ VERIFY2 COMPLETE"
echo "Evidence saved to: ${OUT}"
echo "======================================================================"
