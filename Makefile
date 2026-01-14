.PHONY: run verify clean

run:
	@echo "🚀 Starting KoshaTrack Tactical Engine..."
	@uvicorn src.main:app --host 0.0.0.0 --port 8000 &

verify:
	@echo "🛡️  Executing National Security Audit (V&V Suite)..."
	@bash scripts/test-ssa.sh

clean:
	@echo "🧹 Clearing Environment..."
	-fuser -k 8000/tcp
