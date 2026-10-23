"""Raw flow-cytometry (FCS) and FlowJo workspace ingestion.

Builds a machine-readable index of the raw ICS FCS files (group, condition, event
counts, channels) and reads the FlowJo ``.wsp`` gating hierarchy, so the raw data
behind the study are represented, not only the figure source data. Uses flowio
for fast FCS header/event reads and flowkit for the workspace gating tree.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from . import paths

ICS_DIRS = sorted((paths.DATA_RAW / "zenodo").glob("167*"))


def _parse_name(fname: str) -> dict:
    """ALS/HC group and Negative/Peptide/Positive condition from the file name."""
    group = "ALS" if fname.startswith("ALS") else ("HC" if fname.startswith("HC") else "?")
    cond = next((c for c in ("Negative", "Peptide", "Positive") if c in fname), "?")
    m = re.search(r"_(C\d+)_", fname)
    return {"group": group, "condition": cond, "well": m.group(1) if m else None}


def index_ics_fcs() -> pd.DataFrame:
    """Index every ICS .fcs file: group, condition, event count, channel count."""
    import flowio
    rows = []
    for d in ICS_DIRS:
        for fcs in sorted(d.glob("*.fcs")):
            try:
                fd = flowio.FlowData(str(fcs), ignore_offset_error=True)
                meta = _parse_name(fcs.name)
                rows.append({"record": d.name, "file": fcs.name, **meta,
                             "n_events": fd.event_count,
                             "n_channels": len(fd.channels)})
            except Exception as e:  # pragma: no cover
                rows.append({"record": d.name, "file": fcs.name, "error": str(e)})
    return pd.DataFrame(rows)


def channel_panel(record: str | None = None) -> list[str]:
    """Return the marker/channel panel from the first FCS of a record."""
    import flowio
    d = (paths.DATA_RAW / "zenodo" / record) if record else (ICS_DIRS[0] if ICS_DIRS else None)
    if d is None:
        return []
    fcs = next(iter(sorted(Path(d).glob("*.fcs"))), None)
    if fcs is None:
        return []
    fd = flowio.FlowData(str(fcs), ignore_offset_error=True)
    pns = getattr(fd, "pns_labels", []) or []
    pnn = getattr(fd, "pnn_labels", []) or []
    return [(pns[i] if i < len(pns) and pns[i] else pnn[i] if i < len(pnn) else str(i))
            for i in range(len(pnn))]


def workspace_gating(record: str) -> dict:
    """Read the FlowJo .wsp gating hierarchy for a record (if parseable)."""
    try:
        import flowkit as fk
    except Exception as e:  # pragma: no cover
        return {"error": f"flowkit unavailable: {e}"}
    d = paths.DATA_RAW / "zenodo" / record
    wsp = next(iter(sorted(d.glob("*.wsp"))), None)
    if wsp is None:
        return {"error": "no .wsp found"}
    try:
        ws = fk.Workspace(str(wsp), find_fcs_files_from_wsp=False)
        groups = ws.get_sample_groups()
        gates = {}
        for g in groups:
            try:
                ids = ws.get_gate_ids(g)
                gates[g] = [gid[0] if isinstance(gid, tuple) else gid for gid in ids][:40]
            except Exception:
                pass
        return {"workspace": wsp.name, "sample_groups": list(groups), "gates": gates}
    except Exception as e:
        return {"workspace": wsp.name, "error": str(e)}


def build_index(out_dir: Path | None = None) -> pd.DataFrame:
    out_dir = Path(out_dir or paths.DATASETS)
    df = index_ics_fcs()
    df.to_csv(out_dir / "ics_fcs_index.csv", index=False)
    return df
