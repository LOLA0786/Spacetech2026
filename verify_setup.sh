#!/bin/bash

echo "=== KoshaTrack Setup Verification ==="
echo ""

echo "1. Checking Python version..."
python3 --version

echo ""
echo "2. Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "✓ Virtual environment exists"
else
    echo "✗ Virtual environment not found"
fi

echo ""
echo "3. Checking directory structure..."
if [ -d "ssa_engine/data" ]; then
    echo "✓ ssa_engine/data exists"
else
    echo "✗ ssa_engine/data missing"
fi

echo ""
echo "4. Checking required files..."
files=("main.py" "ssa_engine/data/spacetrack_client.py" "pytest.ini")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
    fi
done

echo ""
echo "5. Testing imports..."
python3 << 'PYEOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

errors = []
try:
    from ssa_engine.data.spacetrack_client import SpaceTrackClient
    print("✓ SpaceTrack client imports")
except ImportError as e:
    errors.append(f"✗ SpaceTrack import failed: {e}")

try:
    from fastapi import FastAPI
    print("✓ FastAPI imports")
except ImportError:
    errors.append("✗ FastAPI not installed")

if errors:
    for error in errors:
        print(error)
PYEOF

echo ""
echo "6. Testing FastAPI app..."
python3 -c "from main import app; print('✓ FastAPI app loads successfully')" 2>&1 | head -5

echo ""
echo "=== Verification Complete ==="
