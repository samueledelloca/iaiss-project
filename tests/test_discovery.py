"""Tests for the agentic discovery loop."""
from __future__ import annotations
import pytest
from c9n2a import discovery, paths

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")

def test_question_bank_has_at_least_20():
    assert len(discovery.QUESTIONS) >= 20

def test_all_layers_present():
    layers = {s.layer for s in discovery.AGENT_SPECS.values()}
    assert {3, 4, 5} <= layers
    kinds = {s.kind for s in discovery.AGENT_SPECS.values()}
    assert {"scientific", "discovery", "pi"} <= kinds

def test_orchestrate_yields_verified_novel_observations():
    res = discovery.orchestrate(backend="cached")
    assert len(res["questions"]) == 24
    assert all(a["verified"] for a in res["questions"])  # all reproduce
    assert len(res["observations"]) >= 5                 # success criterion
    assert res["contradictions"]
