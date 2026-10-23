"""Figure reproduction and discovery figures.

Regenerates the study's major figures from the tidy datasets and draws the
discovery figures for the novel observations. Uses an Okabe-Ito colourblind-safe
palette and a consistent, uncluttered style. Each figure is written as PNG (300
dpi) and PDF.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from . import datasets, stats

mpl.use("Agg")

# Okabe-Ito colourblind-safe palette
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "red": "#D55E00",
      "purple": "#CC79A7", "yellow": "#F0E442", "sky": "#56B4E9", "grey": "#999999"}
GROUP_COLORS = {"HC": OI["sky"], "ALS": OI["red"], "PD": OI["green"], "AD": OI["purple"]}

plt.rcParams.update({
    "figure.dpi": 120, "savefig.dpi": 300, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 11, "axes.titleweight": "bold",
    "legend.frameon": False, "figure.autolayout": True,
})


def _save(fig, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"{name}.png", bbox_inches="tight")
    fig.savefig(out_dir / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def _strip_box(ax, data_by_group, title, ylabel, logy=True):
    groups = list(data_by_group)
    for i, g in enumerate(groups):
        y = np.array(data_by_group[g], dtype=float)
        x = np.random.default_rng(i).normal(i, 0.07, size=len(y))
        ax.scatter(x, y, s=14, color=GROUP_COLORS.get(g, OI["grey"]),
                   alpha=0.7, edgecolor="white", linewidth=0.4, zorder=3)
        ax.hlines(np.median(y), i - 0.25, i + 0.25, color="black", lw=2, zorder=4)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups)
    if logy:
        ax.set_yscale("log")
    ax.set_title(title)
    ax.set_ylabel(ylabel)


def fig_c9orf72_responses(out_dir: Path) -> str:
    """Fig. 2 reproduction: C9orf72 FluoroSpot responses, ALS vs HC, by cytokine."""
    f2 = datasets.load("fig2_fluorospot_responses")
    cytos = ["Total", "IFNg", "IL-5", "IL-10"]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.2))
    for ax, cyto in zip(axes, cytos):
        s = f2[(f2.antigen == "C9orf72") & (f2.cytokine == cyto)]
        d = {g: s[s.group == g].magnitude.tolist() for g in ["HC", "ALS"]}
        r = stats.mann_whitney(d["ALS"], d["HC"])
        _strip_box(ax, d, f"{cyto}\n(p={r.p_value:.3g})", "Response magnitude")
    fig.suptitle("C9orf72-specific FluoroSpot responses in ALS vs HC (reproduction of Fig. 2)",
                 y=1.05, fontweight="bold")
    _save(fig, out_dir, "fig2_c9orf72_responses")
    return "fig2_c9orf72_responses"


def fig_th2_bias(out_dir: Path) -> str:
    """ED Fig. 2 reproduction: IFNg/IL-5 ratio, HC vs ALS."""
    ed = datasets.load("edfig2_ifng_il5_ratio")
    tg = ed[(ed.kind == "two_group") & (ed.measure == "IFNg/IL-5 ratio")]
    d = {g: tg[tg.group == g].value.tolist() for g in ["HC", "ALS"]}
    r = stats.mann_whitney(d["ALS"], d["HC"])
    fig, ax = plt.subplots(figsize=(3.4, 3.4))
    _strip_box(ax, d, f"IFNg/IL-5 ratio (p={r.p_value:.3g})", "IFNg / IL-5", logy=True)
    ax.axhline(1.0, color=OI["grey"], ls="--", lw=0.8)
    _save(fig, out_dir, "edfig2_th2_bias")
    return "edfig2_th2_bias"


def fig_epitope_landscape(out_dir: Path) -> str:
    """Fig. 3 reproduction: immunogenicity across the C9orf72 sequence."""
    pep = datasets.load("si_table1_peptide_screen")
    p = pep[~pep.phospho].sort_values("start_residue")
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.bar(p.start_residue, p.response_freq * 100, width=4,
           color=OI["blue"], alpha=0.85)
    top = p.nlargest(5, "avg_magnitude")
    for _, row in top.iterrows():
        ax.annotate(row.residues, (row.start_residue, row.response_freq * 100),
                    textcoords="offset points", xytext=(0, 4), fontsize=7, ha="center")
    ax.set_xlabel("C9orf72 residue (peptide start)")
    ax.set_ylabel("Response frequency (%)")
    ax.set_title("C9orf72 epitope immunogenicity landscape (reproduction of Fig. 3)")
    _save(fig, out_dir, "fig3_epitope_landscape")
    return "fig3_epitope_landscape"


def fig_hla_immunogenicity(out_dir: Path) -> str:
    """ED Fig. 5 reproduction: predicted HLA binding vs observed immunogenicity."""
    pep = datasets.load("si_table1_peptide_screen")
    p = pep[~pep.phospho & pep.n_predicted_hla_bound.notna()]
    r = stats.spearman(p.n_predicted_hla_bound, p.response_freq)
    fig, ax = plt.subplots(figsize=(3.8, 3.4))
    ax.scatter(p.n_predicted_hla_bound, p.response_freq * 100, s=18,
               color=OI["green"], alpha=0.7, edgecolor="white", linewidth=0.4)
    ax.set_xlabel("Number of predicted HLA-II binders")
    ax.set_ylabel("Response frequency (%)")
    ax.set_title(f"HLA binding vs immunogenicity\n(Spearman rho={r.effect_size:.2f}, p={r.p_value:.3g})")
    _save(fig, out_dir, "edfig5_hla_immunogenicity")
    return "edfig5_hla_immunogenicity"


def fig_survival(out_dir: Path) -> str:
    """Fig. 4 reproduction: IL-10 C9orf72 response by predicted survival."""
    f4 = datasets.load("fig4_mutation_survival")
    fig, axes = plt.subplots(1, 2, figsize=(6, 3.2))
    for ax, cyto in zip(axes, ["IL-10", "IL-5"]):
        s = f4[(f4.analysis == "survival") & (f4.cytokine == cyto)]
        d = {k.capitalize(): s[s.stratum.str.lower() == k].magnitude.tolist()
             for k in ["short", "long"]}
        r = stats.mann_whitney(d["Long"], d["Short"])
        for i, g in enumerate(["Short", "Long"]):
            y = np.array(d[g]); x = np.random.default_rng(i).normal(i, 0.07, len(y))
            ax.scatter(x, y, s=16, color=[OI["red"], OI["blue"]][i], alpha=0.7,
                       edgecolor="white", linewidth=0.4)
            ax.hlines(np.median(y), i - 0.25, i + 0.25, color="black", lw=2)
        ax.set_xticks([0, 1]); ax.set_xticklabels(["Short", "Long"])
        ax.set_yscale("log"); ax.set_title(f"{cyto} (p={r.p_value:.3g})")
        ax.set_ylabel("Response magnitude")
    fig.suptitle("C9orf72 response by predicted survival (reproduction of Fig. 4)",
                 y=1.05, fontweight="bold")
    _save(fig, out_dir, "fig4_survival")
    return "fig4_survival"


def fig_spatial_clustering(out_dir: Path) -> str:
    """Discovery figure: spatial autocorrelation of epitope immunogenicity."""
    from .analyses import epitope_spatial_structure
    a = epitope_spatial_structure()
    pep = datasets.load("si_table1_peptide_screen")
    p = pep[~pep.phospho].sort_values("start_residue")
    resp = p.response_freq.to_numpy() * 100
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.2),
                                   gridspec_kw={"width_ratios": [2, 1]})
    ax1.plot(p.start_residue, resp, color=OI["blue"], lw=1.2, marker="o", ms=3)
    ax1.set_xlabel("C9orf72 residue (peptide start)")
    ax1.set_ylabel("Response frequency (%)")
    ax1.set_title("Immunogenicity along the sequence")
    ax2.scatter(resp[:-1], resp[1:], s=16, color=OI["orange"], alpha=0.7,
                edgecolor="white", linewidth=0.4)
    ax2.set_xlabel("Response freq., peptide i (%)")
    ax2.set_ylabel("Response freq., peptide i+1 (%)")
    ax2.set_title(f"Lag-1 autocorr={a.stats['lag1_autocorr']:.2f}\n(perm p={a.stats['perm_p']:.3g})")
    _save(fig, out_dir, "discovery_spatial_clustering")
    return "discovery_spatial_clustering"


def fig_cross_antigen(out_dir: Path) -> str:
    """Discovery figure: ALS vs HC cytokine enrichment across antigens."""
    f2 = datasets.load("fig2_fluorospot_responses")
    antigens = ["C9orf72", "TDP-43", "SOD1", "EBV"]
    cytos = ["IL-5", "IL-10", "IFNg"]
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    width = 0.25
    for j, cyto in enumerate(cytos):
        rbcs = []
        for ag in antigens:
            s = f2[(f2.antigen == ag) & (f2.cytokine == cyto)]
            r = stats.mann_whitney(s[s.group == "ALS"].magnitude.tolist(),
                                   s[s.group == "HC"].magnitude.tolist())
            rbcs.append(-r.effect_size)  # positive => ALS>HC
        ax.bar(np.arange(len(antigens)) + j * width, rbcs, width,
               label=cyto, color=[OI["red"], OI["blue"], OI["grey"]][j])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(np.arange(len(antigens)) + width)
    ax.set_xticklabels(antigens)
    ax.set_ylabel("ALS>HC effect (rank-biserial)")
    ax.set_title("Cytokine enrichment in ALS is antigen-dependent")
    ax.legend(title="Cytokine")
    _save(fig, out_dir, "discovery_cross_antigen")
    return "discovery_cross_antigen"


ALL_FIGURES = [fig_c9orf72_responses, fig_th2_bias, fig_epitope_landscape,
               fig_hla_immunogenicity, fig_survival,
               fig_spatial_clustering, fig_cross_antigen]


def build_all(out_dir: Path) -> list[str]:
    return [fn(out_dir) for fn in ALL_FIGURES]
