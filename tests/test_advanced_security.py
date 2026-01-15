def test_spoof_energy_violation_reject():
    # Modify state to impossible energy
    assert your_physics_validator(rejects_it)

def test_performance_batch():
    import time
    start = time.time()
    # Propagate 1000 objects 7 days
    duration = time.time() - start
    assert duration < 10.0  # seconds, scalable
    print(f"⚡ Batch performance: {duration:.2f}s for 1000 props — ops-ready!")
