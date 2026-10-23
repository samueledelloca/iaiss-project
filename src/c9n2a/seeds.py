"""Deterministic seeding.

A single call to :func:`set_global_seed` fixes Python's ``random``, NumPy's
legacy global state, and ``PYTHONHASHSEED`` (for child processes), and returns a
NumPy :class:`~numpy.random.Generator` that callers should thread through their
own code for reproducible sampling.
"""
from __future__ import annotations

import os
import random

import numpy as np

DEFAULT_SEED = 1234


def set_global_seed(seed: int = DEFAULT_SEED) -> np.random.Generator:
    """Seed all global RNGs and return a fresh NumPy Generator.

    Note: ``PYTHONHASHSEED`` only takes effect for processes started *after* it
    is set, so it is exported here mainly for subprocesses the pipeline spawns.
    """
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    return np.random.default_rng(seed)
