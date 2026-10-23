"""Provenance capture for reproducible experiment runs.

Each experiment records a manifest holding the git commit, config hash, seed,
interpreter/platform details, selected package versions, and SHA-256 checksums of
its inputs and outputs, so any result can be traced back to the exact state that
produced it.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from . import paths

_TRACKED_PACKAGES = [
    "numpy", "pandas", "scipy", "statsmodels", "scikit-learn",
    "flowkit", "flowio", "biopython", "fastembed", "faiss-cpu",
    "mcp", "anthropic",
]


def sha256_file(path: str | Path, chunk: int = 1 << 20) -> str:
    """SHA-256 of a file, streamed."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def _git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=paths.ROOT, stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return None


def _package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for pkg in _TRACKED_PACKAGES:
        try:
            out[pkg] = version(pkg)
        except PackageNotFoundError:
            out[pkg] = "not-installed"
    return out


def capture_provenance(config: dict[str, Any] | None = None,
                       seed: int | None = None,
                       inputs: dict[str, str | Path] | None = None) -> dict[str, Any]:
    """Build a provenance manifest for the current run."""
    manifest: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "package_versions": _package_versions(),
        "seed": seed,
        "config_hash": (config or {}).get("_hash"),
    }
    if inputs:
        manifest["input_checksums"] = {
            name: sha256_file(p) for name, p in inputs.items() if Path(p).exists()
        }
    return manifest


def write_manifest(run_dir: str | Path, manifest: dict[str, Any],
                   name: str = "provenance.json") -> Path:
    """Write a manifest JSON into ``run_dir`` and return its path."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / name
    with open(out, "w") as fh:
        json.dump(manifest, fh, indent=2, default=str)
    return out
