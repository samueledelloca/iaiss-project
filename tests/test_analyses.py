"""Tests for the analysis library."""
from __future__ import annotations

import pytest
from c9n2a import analyses, datasets, paths

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")


def test_reproductions_match_paper_direction():
    a = analyses.als_vs_hc_response("C9orf72", "Total")
    assert a.stats["p_value"] < 0.05
    assert a.stats["estimates"]["median_x"] > a.stats["estimates"]["median_y"]
    assert "increased in ALS" in a.reproduces


def test_hla_immunogenicity_positive_correlation():
    a = analyses.hla_binding_vs_immunogenicity()
    assert a.stats["effect_size"] > 0 and a.stats["p_value"] < 0.05


def test_jackknife_reports_robustness():
    a = analyses.donor_jackknife("C9orf72", "Total")
    assert 0.0 <= a.stats["frac_sig"] <= 1.0
    assert a.novel


def test_run_all_returns_expected_count():
    res = analyses.run_all()
    assert len(res) == len(analyses.REPRODUCTIONS) + len(analyses.EXPLORATORY)
    assert all(r.finding for r in res)
