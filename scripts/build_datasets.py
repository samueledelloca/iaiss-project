#!/usr/bin/env python3
"""Build all machine-readable datasets from the raw sources.

Parses the Nature source-data workbook (MOESM3), the Supplementary Information
PDF text (S1 peptide screen, S2 HLA typing) and the manuscript JATS tables into
tidy CSVs under ``datasets/``, and writes a provenance manifest.

Usage:  python scripts/build_datasets.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import config, paths, provenance, source_data  # noqa: E402


def main() -> None:
    cfg = config.load_config()
    tables = source_data.build_all()
    manifest = provenance.capture_provenance(cfg, inputs={
        "moesm3_workbook": source_data.WORKBOOK,
        "si_text": source_data.SI_TEXT,
        "jats_xml": source_data.JATS_XML,
    })
    manifest["datasets"] = {name: {"rows": len(df), "columns": list(df.columns)}
                            for name, df in tables.items()}
    (paths.DATASETS / "datasets_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str))
    print(f"Built {len(tables)} datasets under {paths.DATASETS}:")
    for name, df in tables.items():
        print(f"  {name:34s} {len(df):5d} rows")


if __name__ == "__main__":
    main()
