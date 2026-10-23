"""Evaluation-framework tests."""
from __future__ import annotations
import pytest
from c9n2a import evaluation, paths

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")

def test_reproduction_fidelity_matches_authors():
    f = evaluation.reproduction_fidelity()
    assert f["significance_agreement"] == 1.0
    assert f["max_abs_diff"] < 0.005

def test_false_hypotheses_are_rejected():
    t = evaluation.false_hypothesis_test()
    assert t["correctly_rejected"] == t["n"]  # both nulls rejected

def test_grounding_and_determinism():
    assert evaluation.grounding_check()["grounding_rate"] == 1.0
    assert evaluation.determinism_check()["deterministic"]
    assert evaluation.tool_use_accuracy()["accuracy"] == 1.0
