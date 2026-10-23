"""Smoke tests: figures build and write files."""
from __future__ import annotations
import tempfile
from pathlib import Path
import pytest
from c9n2a import figures, paths

pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "fig2_fluorospot_responses.csv").exists(),
    reason="datasets not built")

def test_all_figures_build(tmp_path):
    names = figures.build_all(tmp_path)
    assert len(names) == 7
    for n in names:
        assert (tmp_path / f"{n}.png").exists()
        assert (tmp_path / f"{n}.pdf").exists()
