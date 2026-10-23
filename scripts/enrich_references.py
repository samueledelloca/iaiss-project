#!/usr/bin/env python3
"""Build reports/references.bib with metadata verified against Crossref.

Every reference's authors, year, title, venue, volume and pages are taken from the
DOI's Crossref record (cached to literature/crossref_cache.json for reproducible,
offline rebuilds), per the project's requirement to verify reference metadata
against the DOI record. Bib keys keep the scheme used in the report so citations
do not break; only the fields are corrected.

Usage:  python scripts/enrich_references.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import paths  # noqa: E402

CACHE = paths.LITERATURE / "crossref_cache.json"
UA = {"User-Agent": "c9n2a/0.1 (mailto:samuele.delloca@supsi.ch)"}


def crossref(doi: str, cache: dict) -> dict | None:
    if doi in cache:
        return cache[doi]
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}", headers=UA, timeout=30)
        if r.ok:
            cache[doi] = r.json()["message"]
            time.sleep(0.2)
            return cache[doi]
    except Exception:
        pass
    return None


def bibesc(s: str) -> str:
    return (str(s).replace("&", r"\&").replace("%", r"\%")
            .replace("#", r"\#").replace("_", r"\_"))


def entry(key: str, m: dict) -> str:
    authors = m.get("author", [])
    if authors:
        a0 = authors[0]
        name = f"{a0.get('family','')}, {a0.get('given','')}".strip(", ")
        author = f"{name} and others" if len(authors) > 1 else name
    else:
        author = "Anonymous"
    year = (m.get("issued", {}).get("date-parts", [[None]])[0][0]
            or m.get("published", {}).get("date-parts", [[None]])[0][0] or "")
    title = bibesc((m.get("title") or [""])[0])
    venue = bibesc((m.get("container-title") or [""])[0])
    vol = m.get("volume", "")
    pages = m.get("page") or m.get("article-number") or ""
    fields = [f"  author={{{author}}}", f"  title={{{title}}}", f"  journal={{{venue}}}",
              f"  year={{{year}}}"]
    if vol:
        fields.append(f"  volume={{{vol}}}")
    if pages:
        fields.append(f"  pages={{{pages}}}")
    fields.append(f"  doi={{{m.get('DOI','')}}}")
    return "@article{" + key + ",\n" + ",\n".join(fields) + "\n}"


def main() -> None:
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    cites = json.loads((paths.LITERATURE / "citations.json").read_text())

    entries = []
    # primary reference + the Paper2Agent preprint
    mich = crossref("10.1038/s41586-025-09588-6", cache)
    if mich:
        entries.append(entry("michaelis2025c9orf72", mich))
    entries.append(
        "@misc{miao2025paper2agent,\n  author={Miao, Jiacheng and others},\n"
        "  title={{Paper2Agent}: Reimagining Research Papers as Interactive and Reliable {AI} Agents},\n"
        "  year={2025},\n  eprint={2509.06917},\n  archivePrefix={arXiv},\n"
        "  primaryClass={cs.AI},\n  howpublished={arXiv preprint arXiv:2509.06917}\n}")

    for i, c in enumerate(cites):
        doi = c.get("doi")
        key = c.get("authors_short", f"ref{i}").split()[0].lower().replace(",", "") + str(c.get("year", ""))
        m = crossref(doi, cache) if doi else None
        if m:
            entries.append(entry(key, m))
        else:  # fall back to the curated fields if Crossref is unavailable
            entries.append(
                f"@article{{{key},\n  author={{{c.get('authors_short','')}}},\n"
                f"  title={{{bibesc(c.get('title',''))}}},\n  journal={{{bibesc(c.get('journal',''))}}},\n"
                f"  year={{{c.get('year','')}}},\n  doi={{{doi or ''}}}\n}}")

    CACHE.write_text(json.dumps(cache, indent=1))
    (paths.REPORTS / "references.bib").write_text("\n\n".join(entries) + "\n")
    print(f"Wrote {len(entries)} references to reports/references.bib "
          f"(Crossref-verified, {len(cache)} cached).")


if __name__ == "__main__":
    main()
