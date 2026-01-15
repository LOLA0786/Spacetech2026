verify:
	@echo "Running KoshaTrack verification (tests)..."
	@pytest -q || pytest -v

verify2:
	@echo "Running Verify2 (ISS legacy vs full perturbations)..."
	@bash verify2.sh

verify3:
	@echo "Running Verify3 (GSO/IRNSS drift comparison)..."
	@bash verify3.sh
