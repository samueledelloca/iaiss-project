#!/usr/bin/env python3
"""Regenerate the major study figures and the discovery figures.

Usage:  python scripts/reproduce_figures.py
Writes PNG+PDF to results/figures/ and reports/figures/.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import figures, paths, seeds

def main() -> None:
    seeds.set_global_seed(1234)
    names = figures.build_all(paths.RESULTS / "figures")
    # mirror into the report tree for \includegraphics
    figures.build_all(paths.REPORTS / "figures")
    print(f"Generated {len(names)} figures: {', '.join(names)}")

if __name__ == "__main__":
    main()
