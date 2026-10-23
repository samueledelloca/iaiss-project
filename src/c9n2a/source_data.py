"""Parse the Nature source-data workbook (MOESM3) into tidy, machine-readable tables.

The workbook organises each figure as several side-by-side *panels* (marked a, b,
c, ... in the top row), each panel being a block of columns whose header gives a
series label and whose cells below are per-donor values. This module turns that
layout into long-format CSVs under ``datasets/`` plus a schema description.

A column-centric parser forward-fills the header rows, then for every data column
collects the numeric values beneath it. Per-sheet builders map the raw headers to
semantic fields (cytokine, antigen, group, subset, ...).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

from . import paths

WORKBOOK = paths.DATA_RAW / "supplementary" / "41586_2025_9588_MOESM3_ESM.xlsx"


# --------------------------------------------------------------------------- #
# Generic column-centric parsing
# --------------------------------------------------------------------------- #
def _ffill(seq: list) -> list:
    out, last = [], None
    for v in seq:
        if v is not None and str(v).strip() != "":
            last = v
        out.append(last)
    return out


def _rows(ws) -> list[list]:
    return [list(r) for r in ws.iter_rows(values_only=True)]


def parse_columns(ws, label_row: int, data_row: int,
                   panel_row: int = 0, sub_row: int | None = 1) -> list[dict]:
    """Return one record per data column: panel, sub, label, and its value vector.

    label_row : row index whose cells name each series (not forward-filled).
    data_row  : first row of per-donor values.
    panel_row : row with the panel letters (forward-filled across the width).
    sub_row   : optional measure row (e.g. Total/IFNg), forward-filled within width.
    """
    rows = _rows(ws)
    width = max(len(r) for r in rows)
    def row(i):
        r = rows[i] if i < len(rows) else []
        return list(r) + [None] * (width - len(r))
    panels = _ffill(row(panel_row))
    subs = _ffill(row(sub_row)) if sub_row is not None else [None] * width
    labels = row(label_row)
    out = []
    prev_col = None
    block_id = -1
    for c in range(width):
        lab = labels[c]
        if lab is None or str(lab).strip() == "":
            continue
        values = []
        for i in range(data_row, len(rows)):
            v = rows[i][c] if c < len(rows[i]) else None
            if v is None or (isinstance(v, str) and v.strip() == ""):
                continue
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                values.append(v)  # keep non-numeric (e.g. p-value panels)
        if values:
            # a gap of more than one column (a blank separator) starts a new block,
            # which disambiguates panels that reuse the same letter / measure name.
            if prev_col is None or c - prev_col > 1:
                block_id += 1
            prev_col = c
            out.append({"col": c, "block": block_id, "panel": panels[c],
                        "sub": subs[c], "label": str(lab).strip(), "values": values})
    return out


# --------------------------------------------------------------------------- #
# Per-sheet builders -> tidy long DataFrames
# --------------------------------------------------------------------------- #
_ANTIGENS = {"tdp-43": "TDP-43", "sod1": "SOD1", "c9orf72": "C9orf72",
             "c9Orf72": "C9orf72", "ebv": "EBV"}


def _split_antigen_group(label: str) -> tuple[str | None, str | None]:
    # e.g. "C9Orf72 - ALS", "TDP-43 - HC", "EBV - HC"
    m = re.match(r"\s*(.+?)\s*-\s*(HC|ALS|PD|AD)\s*$", label, flags=re.I)
    if not m:
        return None, None
    ag = _ANTIGENS.get(m.group(1).strip().lower(), m.group(1).strip())
    return ag, m.group(2).upper()


def build_fig2_fluorospot(wb) -> pd.DataFrame:
    recs = parse_columns(wb["Fig. 2"], label_row=2, data_row=3)
    rows = []
    for r in recs:
        cyto = r["sub"]
        if cyto not in {"Total", "IFNg", "IL-5", "IL-10"}:
            continue
        ag, grp = _split_antigen_group(r["label"])
        if ag is None:
            continue
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"cytokine": cyto, "antigen": ag, "group": grp,
                             "donor_idx": i, "magnitude": float(v)})
    return pd.DataFrame(rows)


def build_fig1_subsets(wb) -> pd.DataFrame:
    recs = parse_columns(wb["Fig. 1"], label_row=2, data_row=3)
    rows = []
    for r in recs:
        m = re.match(r"(.+?)\s+(HC|ALS)\s*$", r["label"])
        if not m:
            continue
        subset, grp = m.group(1).strip(), m.group(2)
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"compartment": r["sub"], "subset": subset,
                             "group": grp, "donor_idx": i, "percent": float(v)})
    return pd.DataFrame(rows)


def build_fig3_epitopes(wb) -> pd.DataFrame:
    ws = wb["Fig. 3"]
    rows = _rows(ws)
    out = []
    for r in rows[2:]:
        if r[0] is None:
            continue
        try:
            epi = int(r[0])
        except (TypeError, ValueError):
            continue
        out.append({
            "epitope_num": epi,
            "pct_responded": float(r[1]) if r[1] is not None else np.nan,
            "avg_magnitude": float(r[2]) if r[2] is not None else np.nan,
            "responses_by_donor": float(r[4]) if len(r) > 4 and r[4] is not None else np.nan,
        })
    return pd.DataFrame(out)


def build_fig4_mutation(wb) -> pd.DataFrame:
    recs = parse_columns(wb["Fig. 4"], label_row=2, data_row=3)
    # Blocks 0-3: mutation status (4 strata); 4-7: C9 vs no mutation; 8-11: Short/Long survival.
    analysis = {**{b: "mutation_status" for b in range(0, 4)},
                **{b: "c9_vs_nonmut" for b in range(4, 8)},
                **{b: "survival" for b in range(8, 12)}}
    rows = []
    for r in recs:
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"block": r["block"], "analysis": analysis.get(r["block"], "?"),
                             "cytokine": r["sub"], "stratum": r["label"],
                             "donor_idx": i, "magnitude": float(v)})
    return pd.DataFrame(rows)


def build_edfig2_ifng_il5(wb) -> pd.DataFrame:
    recs = parse_columns(wb["ED Fig. 2"], label_row=2, data_row=3)
    # Blocks 0-2: 2-group panels (HC vs ALS); blocks 3-9: 4-group panels (HC/ALS/PD/AD).
    rows = []
    for r in recs:
        if r["label"] not in {"HC", "ALS", "PD", "AD"}:
            continue
        kind = "two_group" if r["block"] <= 2 else "four_group"
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"block": r["block"], "kind": kind, "measure": r["sub"],
                             "group": r["label"], "donor_idx": i, "value": float(v)})
    return pd.DataFrame(rows)


def build_edfig4_cd4cd8(wb) -> pd.DataFrame:
    recs = parse_columns(wb["ED Fig. 4"], label_row=2, data_row=3)
    rows = []
    for r in recs:
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"block": r["block"], "panel": r["panel"], "sub": r["sub"],
                             "series": r["label"], "donor_idx": i, "value": float(v)})
    return pd.DataFrame(rows)


def build_edfig5_immunogenicity(wb) -> pd.DataFrame:
    recs = parse_columns(wb["ED Fig. 5"], label_row=1, data_row=2)
    rows = []
    for r in recs:
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"block": r["block"], "panel": r["panel"], "series": r["label"],
                             "idx": i, "value": float(v)})
    return pd.DataFrame(rows)


def build_edfig6_clinical(wb) -> pd.DataFrame:
    recs = parse_columns(wb["ED Fig. 6"], label_row=1, data_row=2)
    rows = []
    for r in recs:
        for i, v in enumerate(r["values"]):
            if isinstance(v, (int, float)):
                rows.append({"block": r["block"], "panel": r["panel"], "measure": r["sub"],
                             "series": r["label"], "idx": i, "value": float(v)})
    return pd.DataFrame(rows)


def build_reported_pvalues(wb) -> pd.DataFrame:
    """Authors' reported p-values embedded in the ED Fig. 2 'p values' panel."""
    ws = wb["ED Fig. 2"]
    rows = _rows(ws)
    header = None
    for i, r in enumerate(rows):
        joined = " ".join(str(x) for x in r if x)
        if "Comparison" in joined and "p-value" in joined.lower():
            header = i
            cols = {str(x).strip(): j for j, x in enumerate(r) if x}
            break
    if header is None:
        return pd.DataFrame()
    out = []
    for r in rows[header + 1:]:
        legend = r[cols.get("Figure Legend", 0)]
        comp = r[cols.get("Comparison", 1)]
        if legend is None and comp is None:
            continue
        rawp = r[cols.get("Raw p-value ", cols.get("Raw p-value", 2))]
        out.append({"figure_legend": legend, "comparison": comp, "raw_p": rawp})
    return pd.DataFrame([o for o in out if o["comparison"] is not None])


SI_TEXT = paths.LITERATURE / "paper" / "SI_MOESM1.txt"


def parse_peptide_screen(txt_path: Path | None = None) -> pd.DataFrame:
    """Supplementary Table S1: full screen of all C9orf72 peptides.

    Columns: residues, sequence, phospho flag, responders, tested, response
    frequency, average magnitude, number of predicted HLA binders. Rows are kept
    in screen order, which matches the Fig. 3 epitope numbering (phospho variants
    included), so an ``epitope_num`` index is attached.
    """
    text = Path(txt_path or SI_TEXT).read_text()
    # S1 lies between its caption and the "Boxes indicated mesopools" note.
    start = text.find("Results of the screen of all peptides")
    end = text.find("Boxes indicated mesopools")
    block = text[start:end if end > 0 else None]
    pat = re.compile(
        r"^\s*(\d+-\d+)\s+([A-Z][A-Z*]+)\s+(\d+)/(\d+)\s+([\d.]+)\s+(\d+|N/A)\s*$",
        re.M)
    rows = []
    for m in pat.finditer(block):
        residues, seq, resp, tested, mag, hla = m.groups()
        rows.append({
            "residues": residues,
            "start_residue": int(residues.split("-")[0]),
            "sequence": seq,
            "phospho": "*" in seq,
            "responders": int(resp),
            "tested": int(tested),
            "response_freq": int(resp) / int(tested),
            "avg_magnitude": float(mag),
            "n_predicted_hla_bound": None if hla == "N/A" else int(hla),
        })
    df = pd.DataFrame(rows)
    df.insert(0, "epitope_num", range(1, len(df) + 1))
    return df


def parse_hla_typing(txt_path: Path | None = None) -> pd.DataFrame:
    """Supplementary Table S2: per-donor HLA typing (long format).

    Returns rows of (donor, locus, allele_index, allele). Handles the two
    donor blocks (1-5, 6-10) and the line-wrapped DQA1 cells for donors 6-10.
    """
    lines = Path(txt_path or SI_TEXT).read_text().splitlines()
    try:
        s2 = next(i for i, ln in enumerate(lines) if "HLA typing information" in ln)
    except StopIteration:
        return pd.DataFrame()
    block = lines[s2:]
    records = []
    donors: list[str] = []
    pending_prefix: list[str] = []  # for wrapped cells
    for ln in block:
        if re.search(r"Donor-\d+", ln):
            donors = re.findall(r"Donor-\d+", ln)
            pending_prefix = []
            continue
        m = re.match(r"\s*HLA-(\w+) Allele (\d)\s+(.*)$", ln)
        if m and donors:
            locus, idx, rest = m.groups()
            cells = rest.split()
            if pending_prefix:
                cells = [pending_prefix[j] + cells[j] if j < len(cells) else cells[j]
                         for j in range(len(cells))] if len(pending_prefix) == len(cells) else cells
                pending_prefix = []
            for d, allele in zip(donors, cells):
                records.append({"donor": d, "locus": f"HLA-{locus}",
                                "allele_index": int(idx),
                                "allele": None if allele.lower() == "n/a" else allele})
        elif donors and re.match(r"\s*(DQA1|DQB1|DRB\d|DPB1|DPA1)\*", ln):
            # a wrapped continuation line holding partial allele prefixes
            pending_prefix = ln.split()
    return pd.DataFrame(records)


BUILDERS = {
    "fig1_tcell_subsets": build_fig1_subsets,
    "fig2_fluorospot_responses": build_fig2_fluorospot,
    "fig3_epitopes": build_fig3_epitopes,
    "fig4_mutation_survival": build_fig4_mutation,
    "edfig2_ifng_il5_ratio": build_edfig2_ifng_il5,
    "edfig4_cd4_cd8": build_edfig4_cd4cd8,
    "edfig5_immunogenicity_hla": build_edfig5_immunogenicity,
    "edfig6_clinical_correlates": build_edfig6_clinical,
    "reported_pvalues": build_reported_pvalues,
}


JATS_XML = paths.DATA_RAW / "pmc" / "PMC12657233.jats.xml"


def build_jats_tables() -> dict[str, pd.DataFrame]:
    """Extract the inline manuscript tables (Table 1 epitopes, Table 2 HLA)."""
    import xml.etree.ElementTree as ET
    root = ET.fromstring(JATS_XML.read_bytes())

    def txt(e):
        return " ".join("".join(e.itertext()).split())

    def table_df(label_sub):
        for tw in root.iter("table-wrap"):
            lab = tw.find("label")
            if lab is not None and label_sub.lower() in txt(lab).lower():
                tbl = tw.find(".//table")
                rows = [[txt(td) for td in tr] for tr in tbl.iter("tr")]
                return pd.DataFrame([r for r in rows[1:] if any(r)], columns=rows[0])
        return pd.DataFrame()

    return {
        "table1_epitopes_ge3donors": table_df("Table 1"),
        "table2_hla_restrictions": table_df("Table 2"),
    }


def build_all(out_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    out_dir = Path(out_dir or paths.DATASETS)
    out_dir.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True)
    tables = {}
    for name, fn in BUILDERS.items():
        tables[name] = fn(wb)
    tables["si_table1_peptide_screen"] = parse_peptide_screen()
    tables["si_table2_hla_typing"] = parse_hla_typing()
    tables.update(build_jats_tables())
    for name, df in tables.items():
        df.to_csv(out_dir / f"{name}.csv", index=False)
    return tables


if __name__ == "__main__":
    tabs = build_all()
    for name, df in tabs.items():
        print(f"{name:32s} rows={len(df):5d} cols={list(df.columns)}")
