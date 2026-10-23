#!/usr/bin/env python3
"""Assemble a ready-to-upload Zenodo deposit package.

Bundles the derived datasets, computational results, evaluation, the report and
the deposit metadata into a single zip under dist/ (gitignored). Upload the zip's
contents to a new Zenodo deposit and paste the fields from zenodo/zenodo_metadata.json.

Usage:  python scripts/make_zenodo_package.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import paths  # noqa: E402

OUT = paths.ROOT / "dist"
INCLUDE = [
    ("datasets", "*.csv"), ("datasets", "SCHEMA.md"), ("datasets", "datasets_manifest.json"),
    ("results/analyses", "*"), ("results/discovery", "*"), ("results/model", "*"),
    ("results/figures", "*.png"), ("evaluation", "*.json"),
    ("reports", "main.pdf"), ("literature", "citations.json"), ("data", "DATA_SOURCES.md"),
    ("zenodo", "zenodo_metadata.json"),
]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    zip_path = OUT / "zenodo_c9orf72_nature2agent.zip"
    files: list[Path] = []
    for sub, pat in INCLUDE:
        files.extend(sorted((paths.ROOT / sub).glob(pat)))
    manifest = {}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            if f.is_file():
                arc = f.relative_to(paths.ROOT)
                z.write(f, arc)
                manifest[str(arc)] = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
        # a top-level README for the deposit
        readme = (
            "C9orf72-Nature2Agent - Zenodo deposit\n"
            "=====================================\n\n"
            "Derived datasets and computational results from the Michaelis et al. (2025)\n"
            "Nature C9orf72/ALS study. See zenodo/zenodo_metadata.json for the deposit\n"
            "metadata and datasets/SCHEMA.md for the dataset descriptions.\n\n"
            "Primary data reused under CC-BY 4.0 (attribute Michaelis et al. 2025).\n"
            "Full code: https://github.com/samueledelloca/iaiss-project (MIT).\n")
        z.writestr("README.txt", readme)
        z.writestr("MANIFEST_sha256.json", json.dumps(manifest, indent=2))
    size_mb = zip_path.stat().st_size / 1e6
    print(f"Wrote {zip_path} ({size_mb:.1f} MB, {len(manifest)} files).")
    print("Upload its contents to a new Zenodo deposit; fill the form from "
          "zenodo/zenodo_metadata.json.")


if __name__ == "__main__":
    main()
