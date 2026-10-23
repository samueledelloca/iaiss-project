"""Thin loader for the built datasets under ``datasets/``."""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from . import paths


@lru_cache(maxsize=None)
def load(name: str) -> pd.DataFrame:
    """Load a dataset CSV by its stem (e.g. 'fig2_fluorospot_responses')."""
    path = paths.DATASETS / f"{name}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found; run `python scripts/build_datasets.py` first.")
    return pd.read_csv(path)


def available() -> list[str]:
    return sorted(p.stem for p in paths.DATASETS.glob("*.csv"))
