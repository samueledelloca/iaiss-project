"""Tests for the reproducibility foundation."""
from __future__ import annotations

import numpy as np

from c9n2a import config, paths, provenance, seeds


def test_project_root_has_pyproject():
    assert (paths.ROOT / "pyproject.toml").exists()


def test_seed_is_deterministic():
    g1 = seeds.set_global_seed(1234)
    a = g1.integers(0, 1_000_000, size=5).tolist()
    g2 = seeds.set_global_seed(1234)
    b = g2.integers(0, 1_000_000, size=5).tolist()
    assert a == b
    # legacy global state also reproducible
    seeds.set_global_seed(7)
    x = np.random.rand(3).tolist()
    seeds.set_global_seed(7)
    y = np.random.rand(3).tolist()
    assert x == y


def test_config_loads_and_hashes():
    cfg = config.load_config()
    assert cfg["project"]["name"] == "c9orf72-nature2agent"
    assert cfg["study"]["n_als"] == 40
    assert cfg["study"]["n_hc"] == 28
    assert isinstance(cfg["_hash"], str) and len(cfg["_hash"]) == 12


def test_config_hash_is_order_independent():
    h1 = config.config_hash({"a": 1, "b": {"c": 2, "d": 3}})
    h2 = config.config_hash({"b": {"d": 3, "c": 2}, "a": 1})
    assert h1 == h2


def test_provenance_manifest_fields():
    cfg = config.load_config()
    m = provenance.capture_provenance(cfg, seed=1234)
    for key in ("timestamp_utc", "python_version", "platform",
                "package_versions", "seed", "config_hash"):
        assert key in m
    assert m["seed"] == 1234
    assert m["config_hash"] == cfg["_hash"]
