verify:
	@echo "Running KoshaTrack verification (tests)..."
	@pytest -q || pytest -v

verify2:
	@echo "Running Verify2 (ISS legacy vs full perturbations)..."
	@bash verify2.sh
