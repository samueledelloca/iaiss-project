#!/usr/bin/env python3
"""Run all reproduction and exploratory analyses; persist results + provenance.

Writes:
  results/analyses/reproductions.json   - paper-claim reproductions
  results/analyses/exploratory.json     - exploratory/novel analyses
  results/analyses/summary.md           - human-readable summary
  results/analyses/provenance.json      - run manifest

Usage:  python scripts/run_analyses.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import analyses, config, paths, provenance, seeds  # noqa: E402


def main() -> None:
    cfg = config.load_config()
    seeds.set_global_seed(cfg["reproducibility"]["random_seed"])
    out = paths.RESULTS / "analyses"
    out.mkdir(parents=True, exist_ok=True)

    repro = [f().as_dict() for f in analyses.REPRODUCTIONS]
    explore = [f().as_dict() for f in analyses.EXPLORATORY]
    (out / "reproductions.json").write_text(json.dumps(repro, indent=2, default=str))
    (out / "exploratory.json").write_text(json.dumps(explore, indent=2, default=str))

    lines = ["# Analysis results\n",
             "## Reproductions of the paper's claims\n"]
    for a in repro:
        lines.append(f"- **{a['id']}**: {a['finding']}  \n  _reproduces:_ {a['reproduces']}")
    lines.append("\n## Exploratory analyses (candidate novel observations)\n")
    for a in explore:
        lines.append(f"- **{a['id']}**: {a['finding']}")
    (out / "summary.md").write_text("\n".join(lines) + "\n")

    provenance.write_manifest(out, provenance.capture_provenance(
        cfg, seed=cfg["reproducibility"]["random_seed"]))
    print(f"Wrote {len(repro)} reproductions and {len(explore)} exploratory analyses to {out}")


if __name__ == "__main__":
    main()
