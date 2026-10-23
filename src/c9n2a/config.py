"""Typed project configuration loaded from YAML.

``configs/base.yaml`` holds the defaults; an optional override file is deep-merged
on top. The resulting config carries a stable content hash so every experiment
run can record exactly which configuration produced it.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from . import paths


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def config_hash(config: dict[str, Any]) -> str:
    """Stable short hash of a config dict (order-independent)."""
    payload = json.dumps(config, sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def load_config(override: str | Path | None = None) -> dict[str, Any]:
    """Load ``configs/base.yaml`` and deep-merge an optional override file."""
    base_path = paths.CONFIGS / "base.yaml"
    with open(base_path) as fh:
        config = yaml.safe_load(fh) or {}
    if override is not None:
        override = Path(override)
        if not override.is_absolute():
            override = paths.CONFIGS / override
        with open(override) as fh:
            config = _deep_merge(config, yaml.safe_load(fh) or {})
    config["_hash"] = config_hash({k: v for k, v in config.items() if k != "_hash"})
    return config
