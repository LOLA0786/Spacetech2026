.PHONY: help install run test verify clean

# Default action: show help
help:
	@echo "KoshaTrack SSA Engine - Sovereign Command Menu"
	@echo "---------------------------------------------"
	@echo "make install  - Install dependencies"
	@echo "make run      - Start the FastAPI server"
	@echo "make verify   - Run the Gold Test Suite (Audit Mode)"
	@echo "make clean    - Stop server and clear ports"

install:
	pip install -r requirements.txt

run:
	@echo "Starting KoshaTrack Engine on port 8000..."
	uvicorn src.main:app --host 0.0.0.0 --port 8000 &

verify:
	@echo "Initiating National Security Audit (Gold Test Pack)..."
	@bash scripts/test-ssa.sh

clean:
	@echo "Securing environment and clearing ports..."
	-fuser -k 8000/tcp
	@echo "Port 8000 cleared."
