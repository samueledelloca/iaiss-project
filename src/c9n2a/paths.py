"""Canonical project paths.

The project root is located by walking up from this file until a directory
containing ``pyproject.toml`` is found, so paths resolve correctly whether code
is run from a notebook, a script, or an installed console entry point.
"""
from __future__ import annotations

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Return the repository root (the directory holding ``pyproject.toml``)."""
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: two levels up from src/c9n2a/paths.py
    return Path(__file__).resolve().parents[2]


ROOT = find_project_root()

AGENTS = ROOT / "agents"
MODEL = ROOT / "model"
DATA = ROOT / "data"
DATA_RAW = DATA / "raw"
DATASETS = ROOT / "datasets"
LITERATURE = ROOT / "literature"
NOTEBOOKS = ROOT / "notebooks"
TRAINING = ROOT / "training"
EVALUATION = ROOT / "evaluation"
EXPERIMENTS = ROOT / "experiments"
CONFIGS = ROOT / "configs"
RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"

ALL_DIRS = [
    AGENTS, MODEL, DATA, DATA_RAW, DATASETS, LITERATURE, NOTEBOOKS,
    TRAINING, EVALUATION, EXPERIMENTS, CONFIGS, RESULTS, REPORTS,
]


def ensure_dirs() -> None:
    """Create the standard project directories if they do not yet exist."""
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)
