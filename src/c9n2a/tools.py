"""Shared computational tools for the C9orf72 agent.

One implementation, consumed by both the MCP server (``model/mcp_server.py``) and
the in-process agents. Every tool returns a JSON-serialisable dict and is covered
by the validation tests in ``tests/test_tools.py`` (the Paper2Agent-style
validation loop). Tools are registered in ``TOOLS`` with a short schema so agents
and the MCP server can enumerate them.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Callable

import pandas as pd

from . import analyses, datasets, paths, stats

# C9orf72 long isoform (UniProt Q96LT7-1, 481 aa), for epitope mapping.
C9ORF72_SEQUENCE = (
    "MSTLCPPPSPAVAKTEIALSGKSPLLAATFAYWDNILGPRVRHIWAPKTEQVLLSDGEITFLANHTLNGEILRNAESGAIDVKFF"
    "VLSEKGVIIVSLIFDGNWNGDRSTYGLSIILPQTELSFYLPLHRVCVDRLTHIIRKGRIWMHKERQENVQKIILEGTERMEDQGQ"
    "SIIPMLTGEVIPVMELLSSMKSHSVPEEIDIADTVLNDDDIGDSCHEGFLLNAISSHLQTCGCSVVVGSSAEKVNKIVRTLCLFL"
    "TPAERKCSRLCEAESSFKYESGLFVQGLLKDSTGSFVLPFRQVMYAPYPTTHIDVDVNTVKQMPPCHEHIYNQRRYMRSELTAFW"
    "RATSEEDMAQDTIIYTDESFTPDLNIFQDVLHRDTLVKAFLDQVFQLKPGLSLRSTFLAQFLLVLHRKALTLIKYIEDDTQKGKK"
    "PFKSLRNLKIDLDLTAEGDLNIIMALAEKIKPGLHSFIFGRPFYTSVQERDVLMTF")


def _jats_section(title: str) -> str:
    xml = (paths.DATA_RAW / "pmc" / "PMC12657233.jats.xml")
    if not xml.exists():
        return ""
    root = ET.fromstring(xml.read_bytes())
    for sec in root.iter("sec"):
        t = sec.find("title")
        if t is not None and "".join(t.itertext()).strip().lower() == title.lower():
            return " ".join("".join(sec.itertext()).split())[len(title):].strip()
    return ""


# --------------------------------------------------------------------------- #
# Tool implementations
# --------------------------------------------------------------------------- #
def explain_experimental_design() -> dict:
    """Summarise the study design, cohorts, assays and statistics."""
    return {
        "study": "Michaelis et al. (2025) Nature, DOI 10.1038/s41586-025-09588-6",
        "cohorts": "40 ALS, 28 HC (plus PD/AD and a UCSD validation cohort)",
        "antigens": ["C9orf72 (100 tiling peptides)", "TDP-43", "SOD1", "EBV (control)"],
        "assays": {
            "FluoroSpot": "IFNg/IL-5/IL-10 spot responses after 2-week antigen expansion",
            "ICS": "intracellular cytokine staining (Fortessa) for phenotyping",
            "Spectral": "Cytek Aurora immunophenotyping of T-helper subsets",
        },
        "hla": "IEDB NetMHCIIpan-4.1 EL binding (<=20% percentile); RATE for restriction",
        "statistics": _jats_section("Statistical analysis") or
                      "Two-tailed Mann-Whitney, one-way ANOVA + Dunnett, Fisher exact, Spearman",
    }


def list_datasets() -> dict:
    return {"datasets": datasets.available()}


def describe_dataset(name: str) -> dict:
    df = datasets.load(name)
    return {"name": name, "rows": len(df), "columns": list(df.columns),
            "head": df.head(5).to_dict("records")}


def query_dataset(name: str, filters: dict | None = None, limit: int = 50) -> dict:
    df = datasets.load(name)
    if filters:
        for k, v in filters.items():
            df = df[df[k] == v]
    return {"name": name, "n_matched": len(df),
            "rows": df.head(limit).to_dict("records")}


def epitope_table(min_responders: int = 3, antigen: str = "C9orf72") -> dict:
    """Epitopes recognised by at least ``min_responders`` donors, ranked by breadth."""
    pep = datasets.load("si_table1_peptide_screen")
    sel = pep[pep.responders >= min_responders].sort_values(
        ["responders", "avg_magnitude"], ascending=False)
    return {"n": len(sel), "epitopes": sel.to_dict("records")}


def most_immunogenic_epitopes(top: int = 10) -> dict:
    """Most broadly immunogenic C9orf72 epitopes (by response frequency and magnitude)."""
    pep = datasets.load("si_table1_peptide_screen")
    by_breadth = pep.nlargest(top, "response_freq")[
        ["epitope_num", "residues", "sequence", "responders", "tested",
         "response_freq", "avg_magnitude", "n_predicted_hla_bound"]]
    return {"top_by_breadth": by_breadth.to_dict("records")}


def broadest_hla_coverage(top: int = 10) -> dict:
    """Peptides with the broadest predicted HLA-II coverage."""
    pep = datasets.load("si_table1_peptide_screen")
    sel = pep.dropna(subset=["n_predicted_hla_bound"]).nlargest(top, "n_predicted_hla_bound")
    return {"top_by_hla_coverage": sel[
        ["epitope_num", "residues", "sequence", "n_predicted_hla_bound",
         "response_freq"]].to_dict("records")}


def hla_typing(donor: str | None = None) -> dict:
    hla = datasets.load("si_table2_hla_typing")
    if donor:
        hla = hla[hla.donor == donor]
    return {"n_rows": len(hla), "rows": hla.to_dict("records")}


def reproduce_claim(claim: str = "C9orf72_Total") -> dict:
    """Reproduce a headline claim. claim in {C9orf72_<cyto>, th2_bias, mutation,
    survival, specificity, hla_immunogenicity}."""
    mapping = {
        "th2_bias": analyses.cytokine_th2_bias,
        "mutation": lambda: analyses.mutation_carrier_effect("Total"),
        "survival": lambda: analyses.survival_association("IL-10"),
        "specificity": lambda: analyses.als_specificity_vs_pd_ad("Total"),
        "hla_immunogenicity": analyses.hla_binding_vs_immunogenicity,
    }
    if claim in mapping:
        return mapping[claim]().as_dict()
    if claim.startswith("C9orf72_"):
        return analyses.als_vs_hc_response("C9orf72", claim.split("_", 1)[1]).as_dict()
    raise ValueError(f"unknown claim '{claim}'")


def compare_groups(dataset: str, value_col: str, group_col: str,
                   group_a: str, group_b: str, filters: dict | None = None) -> dict:
    """Generic two-tailed Mann-Whitney between two groups in a dataset."""
    df = datasets.load(dataset)
    if filters:
        for k, v in filters.items():
            df = df[df[k] == v]
    a = df[df[group_col] == group_a][value_col].tolist()
    b = df[df[group_col] == group_b][value_col].tolist()
    return stats.mann_whitney(a, b).as_dict()


def run_analysis(analysis_id: str) -> dict:
    """Run any registered named analysis by id (reproduction or exploratory)."""
    for fn in analyses.REPRODUCTIONS + analyses.EXPLORATORY:
        a = fn()
        if a.id == analysis_id:
            return a.as_dict()
    raise ValueError(f"unknown analysis id '{analysis_id}'")


def list_analyses() -> dict:
    out = []
    for kind, fns in [("reproduction", analyses.REPRODUCTIONS),
                      ("exploratory", analyses.EXPLORATORY)]:
        for fn in fns:
            a = fn()
            out.append({"id": a.id, "kind": kind, "question": a.question, "novel": a.novel})
    return {"analyses": out}


def reported_pvalues() -> dict:
    """The authors' own reported p-values (for validation)."""
    return {"rows": datasets.load("reported_pvalues").to_dict("records")}


def protein_sequence() -> dict:
    return {"uniprot": "Q96LT7-1", "length": len(C9ORF72_SEQUENCE),
            "sequence": C9ORF72_SEQUENCE}


def search_paper(query: str, k: int = 5) -> dict:
    """Retrieve passages from the paper + supplementary (scientific RAG)."""
    from . import rag
    return {"query": query, "passages": rag.get_index().query(query, k=k)}


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
@dataclass
class Tool:
    name: str
    fn: Callable
    description: str


TOOLS: dict[str, Tool] = {t.name: t for t in [
    Tool("explain_experimental_design", explain_experimental_design,
         "Summarise study design, cohorts, assays and statistical methods."),
    Tool("list_datasets", list_datasets, "List available machine-readable datasets."),
    Tool("describe_dataset", describe_dataset, "Schema + head of a dataset."),
    Tool("query_dataset", query_dataset, "Filter and return rows of a dataset."),
    Tool("epitope_table", epitope_table, "Epitopes recognised by >= N donors."),
    Tool("most_immunogenic_epitopes", most_immunogenic_epitopes,
         "Most broadly immunogenic C9orf72 epitopes."),
    Tool("broadest_hla_coverage", broadest_hla_coverage,
         "Peptides with the broadest predicted HLA-II coverage."),
    Tool("hla_typing", hla_typing, "Per-donor HLA typing (HLA-I and HLA-II)."),
    Tool("reproduce_claim", reproduce_claim, "Reproduce a headline claim of the paper."),
    Tool("compare_groups", compare_groups, "Two-tailed Mann-Whitney between two groups."),
    Tool("run_analysis", run_analysis, "Run a named analysis by id."),
    Tool("list_analyses", list_analyses, "List all named analyses."),
    Tool("reported_pvalues", reported_pvalues, "Authors' reported p-values (validation)."),
    Tool("protein_sequence", protein_sequence, "C9orf72 protein sequence (UniProt Q96LT7)."),
    Tool("search_paper", search_paper, "Retrieve passages from the paper + SI (scientific RAG)."),
]}


def call(tool_name: str, **kwargs) -> dict:
    if tool_name not in TOOLS:
        raise KeyError(f"unknown tool '{tool_name}'")
    return TOOLS[tool_name].fn(**kwargs)
