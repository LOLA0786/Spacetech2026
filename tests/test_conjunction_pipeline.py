import numpy as np
# from src.ssa_engine.conjunction.pipeline import conjunction_pipeline

def synthetic_catalog(n_objects=100):
    # Generate random LEO/GSO states + one known close approach
    ...

def test_pipeline_finds_injected_risks():
    risks = conjunction_pipeline(..., catalog=synthetic_catalog())
    assert len(risks) >= 1
    assert risks[0]['miss_distance_m'] < 500.0
    print("🚨 Pipeline nailed high-risk conjunctions in 100-object catalog!")
