#!/usr/bin/env python3
"""Fetch and checksum-verify the Michaelis et al. (2025) primary datasets.

Downloads the five Zenodo deposits (spectral + four ICS screens) into
``data/raw/zenodo/<record_id>/``, verifying each file's MD5 against the Zenodo
record metadata, and records a provenance manifest per record. Re-running skips
files already present with a matching checksum (resumable).

Usage:
    python scripts/fetch_data.py --records all
    python scripts/fetch_data.py --records ics      # the four ICS screens only
    python scripts/fetch_data.py --records 16754609 # a single record
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import paths  # noqa: E402

# Curated Michaelis et al. (2025) Zenodo deposits (verified by title + DOI).
RECORDS = {
    "16749283": {"label": "spectral", "title": "Spectral data"},
    "16749334": {"label": "ics_screen1", "title": "ICS data Screen 1"},
    "16754553": {"label": "ics_screen2", "title": "ICS data Screen 2"},
    "16754591": {"label": "ics_screen3", "title": "ICS data Screen 3"},
    "16754609": {"label": "ics_screen4", "title": "ICS data Screen 4"},
}
ICS_RECORDS = [r for r, m in RECORDS.items() if m["label"].startswith("ics")]
ZENODO_API = "https://zenodo.org/api/records/{rid}"
UA = {"User-Agent": "c9n2a/0.1 (research; samuele.delloca@supsi.ch)"}


def md5_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def record_metadata(rid: str) -> dict:
    r = requests.get(ZENODO_API.format(rid=rid), headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()


def download_file(url: str, dest: Path, expected_md5: str | None) -> dict:
    if dest.exists() and expected_md5 and md5_file(dest) == expected_md5:
        return {"status": "cached", "bytes": dest.stat().st_size}
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, headers=UA, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as fh:
            for chunk in r.iter_content(chunk_size=1 << 20):
                fh.write(chunk)
    got = md5_file(tmp)
    if expected_md5 and got != expected_md5:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"MD5 mismatch for {dest.name}: {got} != {expected_md5}")
    tmp.rename(dest)
    return {"status": "downloaded", "bytes": dest.stat().st_size, "md5": got}


def fetch_record(rid: str) -> dict:
    meta = record_metadata(rid)
    out_dir = paths.DATA_RAW / "zenodo" / rid
    out_dir.mkdir(parents=True, exist_ok=True)
    files_manifest = []
    for f in meta.get("files", []):
        key = f["key"]
        expected = (f.get("checksum") or "").removeprefix("md5:")
        url = f["links"].get("self") or f["links"].get("download")
        info = download_file(url, out_dir / key, expected or None)
        files_manifest.append({"key": key, "md5": expected, **info})
        print(f"  [{info['status']:>10}] {key}  ({info['bytes']/1e6:.1f} MB)")
    manifest = {
        "record_id": rid,
        "doi": meta.get("doi"),
        "conceptdoi": meta.get("conceptdoi"),
        "title": meta["metadata"]["title"],
        "license": meta["metadata"].get("license", {}),
        "publication_date": meta["metadata"].get("publication_date"),
        "files": files_manifest,
    }
    with open(out_dir / "provenance.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--records", default="ics",
                    help="'all', 'ics', or a comma-separated list of record ids")
    args = ap.parse_args()
    if args.records == "all":
        rids = list(RECORDS)
    elif args.records == "ics":
        rids = ICS_RECORDS
    else:
        rids = [r.strip() for r in args.records.split(",")]
    total = 0
    for rid in rids:
        print(f"== Record {rid} ({RECORDS.get(rid, {}).get('title', '?')}) ==")
        m = fetch_record(rid)
        total += sum(f["bytes"] for f in m["files"])
    print(f"\nDone. {len(rids)} record(s), {total/1e6:.1f} MB total, "
          f"under {paths.DATA_RAW / 'zenodo'}")


if __name__ == "__main__":
    main()
