#!/usr/bin/env bash
set -euo pipefail

SSA_URL="${SSA_URL:-http://localhost:8000}"
SIG="SOVEREIGN_AUTH_0786"

echo "=== KoshaTrack National Security Audit (V&V) ==="

# 1. Health Check (Root)
echo "Testing Root Endpoint..."
curl -sSf "$SSA_URL/" > /dev/null || { echo "❌ Server not responding at $SSA_URL"; exit 1; }
echo "✅ Root Endpoint Active"

# 2. Test Function
req() {
  local name="$1"
  local payload="$2"
  local expect="$3"
  
  echo -n "TEST: $name... "
  RESP=$(curl -s -X POST "$SSA_URL/ssa/verify" \
    -H "Content-Type: application/json" \
    -d "$payload")
  
  if echo "$RESP" | grep -q "$expect"; then
    echo "✅ PASS"
  else
    echo "❌ FAIL"
    echo "Expected: $expect"
    echo "Got: $RESP"
    exit 1
  fi
}

# --- PHYSICAL VALIDATION TESTS ---
req "GEO Orbit Integrity" '{"norad_id":49330,"semi_major_axis":42164,"eccentricity":0.0001,"inclination":5.3,"data_signature":"'$SIG'"}' "VERIFIED"
req "LEO Orbit Integrity" '{"norad_id":44797,"semi_major_axis":6745,"eccentricity":0.01,"inclination":97.9,"data_signature":"'$SIG'"}' "VERIFIED"
req "Hyperbolic Reject (e>1)" '{"norad_id":999,"semi_major_axis":7000,"eccentricity":1.2,"inclination":98,"data_signature":"'$SIG'"}' "PHYSICS_VIOLATION"
req "Negative Eccentricity Reject" '{"norad_id":998,"semi_major_axis":7000,"eccentricity":-0.2,"inclination":98,"data_signature":"'$SIG'"}' "PHYSICS_VIOLATION"
req "Auth Reject (Bad Sig)" '{"norad_id":997,"semi_major_axis":7000,"eccentricity":0.01,"inclination":98,"data_signature":"BAD_ACTOR"}' "SECURITY_VIOLATION"

echo ""
echo "🏁 ✅ ALL NATIONAL SECURITY TESTS PASSED"
