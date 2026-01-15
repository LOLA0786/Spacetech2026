#!/bin/bash
# KoshaTrack SSA Engine - Installation Script
# For Government of India deployment
# Supports: Ubuntu 22.04 LTS, CentOS 8+, macOS, Windows (via WSL)

set -e  # Exit on error

echo "======================================================================"
echo "  KoshaTrack SSA Engine - Installation"
echo "  Sovereign Space Situational Awareness for India"
echo "======================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}Error: Python 3.10 or higher required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $python_version found${NC}"

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider using a regular user.${NC}"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p data/tles
mkdir -p data/catalogs
mkdir -p data/reports
mkdir -p logs
mkdir -p config
echo -e "${GREEN}✓ Directories created${NC}"

# Download sample data (if available)
echo ""
echo "Downloading sample data..."
if [ -f "scripts/download_sample_data.py" ]; then
    python scripts/download_sample_data.py
else
    echo -e "${YELLOW}Sample data script not found. Skipping.${NC}"
fi

# Run tests
echo ""
echo "Running test suite to verify installation..."
python -m pytest tests/ -v --tb=short || {
    echo -e "${YELLOW}Warning: Some tests failed. Installation complete but verify functionality.${NC}"
}
echo -e "${GREEN}✓ Tests completed${NC}"

# Create launcher script
echo ""
echo "Creating launcher script..."
cat > koshatrack.sh << 'EOF'
#!/bin/bash
# KoshaTrack launcher

# Activate virtual environment
source "$(dirname "$0")/venv/bin/activate"

# Run KoshaTrack
python "$(dirname "$0")/koshatrack.py" "$@"
