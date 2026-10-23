"""Validation loop for the computational tools (Paper2Agent-style)."""
from __future__ import annotations
import pytest
from c9n2a import paths, tools

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")


def test_every_tool_runs_and_returns_dict():
    defaults = {
        "describe_dataset": {"name": "fig3_epitopes"},
        "query_dataset": {"name": "si_table1_peptide_screen", "filters": {"epitope_num": 14}},
        "hla_typing": {"donor": "Donor-1"},
        "compare_groups": {"dataset": "fig2_fluorospot_responses", "value_col": "magnitude",
                           "group_col": "group", "group_a": "ALS", "group_b": "HC",
                           "filters": {"antigen": "C9orf72", "cytokine": "Total"}},
        "run_analysis": {"analysis_id": "repro_fig2_C9orf72_Total"},
        "reproduce_claim": {"claim": "th2_bias"},
        "search_paper": {"query": "survival", "k": 2},
    }
    for name in tools.TOOLS:
        out = tools.call(name, **defaults.get(name, {}))
        assert isinstance(out, dict) and out


def test_protein_sequence_matches_peptide_positions():
    seq = tools.protein_sequence()["sequence"]
    assert len(seq) == 481
    # epitope 56-70 must be DGEITFLANHTLNGE
    assert seq[55:70] == "DGEITFLANHTLNGE"


def test_reproduce_claim_c9orf72_significant():
    out = tools.reproduce_claim("C9orf72_IL-5")
    assert out["stats"]["p_value"] < 0.05


def test_epitope_table_includes_top_epitope():
    out = tools.epitope_table(min_responders=3)
    assert any(e["residues"] == "56-70" for e in out["epitopes"])
