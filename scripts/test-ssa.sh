#!/usr/bin/env bash
set -euo pipefail

SSA_URL="${SSA_URL:-http://localhost:8000}"
SIG="${SIG:-SOVEREIGN_AUTH_0786}"

pass(){ echo "✅ $1"; }
fail(){ echo "❌ $1"; exit 1; }

req() {
  local name="$1"
  local payload="$2"
  local expect="$3"

  echo ""
  echo "=== TEST: $name ==="
  echo "$payload" | jq . >/dev/null 2>&1 || fail "payload is not valid json"
  RESP=$(curl -sS -X POST "$SSA_URL/ssa/verify" -H "Content-Type: application/json" -d "$payload" || true)

  echo "$RESP" | jq . >/dev/null 2>&1 || fail "response not json: $RESP"

  if echo "$RESP" | grep -q "$expect"; then
    pass "$name"
  else
    echo "---- expected to contain ----"
    echo "$expect"
    echo "---- got ----"
    echo "$RESP"
    fail "$name"
  fi
}

echo "=== KoshaTrack SSA Gold Test ==="
echo "SSA_URL=$SSA_URL"
echo ""

command -v jq >/dev/null 2>&1 || fail "jq missing. install: sudo apt-get update && sudo apt-get install -y jq"

# ---------- GOOD CASES ----------
req "GEO circular sanity" \
"{
  \"norad_id\": 49330,
  \"semi_major_axis\": 42164.0,
  \"eccentricity\": 0.0001,
  \"inclination\": 5.3,
  \"data_signature\": \"$SIG\"
}" \
"\"status\":\"VERIFIED\""

req "LEO SSO sanity" \
"{
  \"norad_id\": 44797,
  \"semi_major_axis\": 6745.0,
  \"eccentricity\": 0.01,
  \"inclination\": 97.9,
  \"data_signature\": \"$SIG\"
}" \
"\"status\":\"VERIFIED\""

req "MEO GPS-like sanity" \
"{
  \"norad_id\": 99901,
  \"semi_major_axis\": 26560.0,
  \"eccentricity\": 0.01,
  \"inclination\": 55.0,
  \"data_signature\": \"$SIG\"
}" \
"\"status\":\"VERIFIED\""

req "GTO-ish eccentric sanity" \
"{
  \"norad_id\": 99902,
  \"semi_major_axis\": 24300.0,
  \"eccentricity\": 0.70,
  \"inclination\": 27.0,
  \"data_signature\": \"$SIG\"
}" \
"\"status\":\"VERIFIED\""

# ---------- BAD / REJECT CASES ----------
req "Physics reject: hyperbolic ecc>1" \
"{
  \"norad_id\": 99999,
  \"semi_major_axis\": 7000.0,
  \"eccentricity\": 1.2,
  \"inclination\": 98.0,
  \"data_signature\": \"$SIG\"
}" \
"PHYSICS_VIOLATION"

req "Physics reject: negative eccentricity" \
"{
  \"norad_id\": 99998,
  \"semi_major_axis\": 7000.0,
  \"eccentricity\": -0.2,
  \"inclination\": 98.0,
  \"data_signature\": \"$SIG\"
}" \
"PHYSICS_VIOLATION"

req "Physics reject: inclination out of bounds (>180)" \
"{
  \"norad_id\": 99997,
  \"semi_major_axis\": 7000.0,
  \"eccentricity\": 0.01,
  \"inclination\": 181.0,
  \"data_signature\": \"$SIG\"
}" \
"PHYSICS_VIOLATION"

req "Auth reject: bad signature" \
"{
  \"norad_id\": 99996,
  \"semi_major_axis\": 7000.0,
  \"eccentricity\": 0.01,
  \"inclination\": 98.0,
  \"data_signature\": \"WRONG_SIG\"
}" \
"SECURITY_VIOLATION"

echo ""
echo "🏁 ✅ ALL SSA GOLD TESTS PASSED"
