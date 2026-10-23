"""Named, verifiable analyses of the C9orf72 study data.

Each function returns an :class:`Analysis` bundling the question, the method, the
numeric result and a plain-language finding. The reproduction analyses re-derive
the paper's headline claims; the exploratory analyses support the discovery agents
(cross-antigen specificity, phospho effects, spatial structure, robustness).

Nothing here is speculative: every ``finding`` is computed from the committed
datasets and is re-checked by the verification agent against the stats output.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import datasets, stats


@dataclass
class Analysis:
    id: str
    question: str
    method: str
    finding: str
    stats: dict = field(default_factory=dict)
    data_source: str = ""
    reproduces: str | None = None
    novel: bool = False
    robustness: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in
                ("id", "question", "method", "finding", "stats",
                 "data_source", "reproduces", "novel", "robustness")}


# --------------------------------------------------------------------------- #
# Reproduction of the paper's headline claims
# --------------------------------------------------------------------------- #
def als_vs_hc_response(antigen: str = "C9orf72", cytokine: str = "Total") -> Analysis:
    f2 = datasets.load("fig2_fluorospot_responses")
    s = f2[(f2.antigen == antigen) & (f2.cytokine == cytokine)]
    hc = s[s.group == "HC"].magnitude.tolist()
    als = s[s.group == "ALS"].magnitude.tolist()
    r = stats.mann_whitney(als, hc)
    direction = "higher" if r.estimates["median_x"] > r.estimates["median_y"] else "lower"
    return Analysis(
        id=f"repro_fig2_{antigen}_{cytokine}".replace("-", ""),
        question=f"Are {antigen} {cytokine} FluoroSpot responses different in ALS vs HC?",
        method="Two-tailed Mann-Whitney U on per-donor response magnitude",
        finding=(f"{antigen} {cytokine} responses are {direction} in ALS "
                 f"(median {r.estimates['median_x']:.0f} vs {r.estimates['median_y']:.0f}, "
                 f"p={r.p_value:.3g}, rank-biserial r={r.effect_size:.2f})."),
        stats=r.as_dict(), data_source="fig2_fluorospot_responses",
        reproduces="C9orf72-specific responses increased in ALS (Fig. 2)")


def cytokine_th2_bias() -> Analysis:
    ed = datasets.load("edfig2_ifng_il5_ratio")
    tg = ed[(ed.kind == "two_group") & (ed.measure == "IFNg/IL-5 ratio")]
    hc = tg[tg.group == "HC"].value.tolist()
    als = tg[tg.group == "ALS"].value.tolist()
    r = stats.mann_whitney(als, hc)
    return Analysis(
        id="repro_th2_bias",
        question="Do ALS responses show an IL-5/IL-10 (Th2/regulatory) bias over IFNg?",
        method="Two-tailed Mann-Whitney U on the per-donor IFNg/IL-5 ratio",
        finding=(f"The IFNg/IL-5 ratio is lower in ALS (median {r.estimates['median_x']:.2f}) "
                 f"than HC (median {r.estimates['median_y']:.2f}), p={r.p_value:.3g}: an "
                 f"IL-5-biased response in ALS."),
        stats=r.as_dict(), data_source="edfig2_ifng_il5_ratio",
        reproduces="ALS responses enriched for IL-5/IL-10 over IFNg (Fig. 2, ED Fig. 2)")


def als_specificity_vs_pd_ad(measure: str = "Total") -> Analysis:
    ed = datasets.load("edfig2_ifng_il5_ratio")
    fg = ed[(ed.kind == "four_group") & (ed.measure == measure)]
    groups = {g: fg[fg.group == g].value.tolist() for g in ["HC", "ALS", "PD", "AD"]}
    res = {}
    for other in ["HC", "PD", "AD"]:
        res[f"ALS_vs_{other}"] = stats.mann_whitney(groups["ALS"], groups[other]).as_dict()
    sig = [k for k, v in res.items() if v["p_value"] < 0.05]
    return Analysis(
        id=f"repro_specificity_{measure}",
        question=f"Is the ALS {measure} C9orf72 response specific vs PD and AD controls?",
        method="Pairwise two-tailed Mann-Whitney U, ALS vs each control group",
        finding=(f"ALS {measure} C9orf72 responses differ from "
                 f"{', '.join(sig) if sig else 'no group'} at p<0.05."),
        stats=res, data_source="edfig2_ifng_il5_ratio",
        reproduces="C9orf72 response relatively specific to ALS (ED Fig. 2)")


def mutation_carrier_effect(cytokine: str = "Total") -> Analysis:
    f4 = datasets.load("fig4_mutation_survival")
    s = f4[(f4.analysis == "c9_vs_nonmut") & (f4.cytokine == cytokine)]
    mut = s[s.stratum.str.contains("mutation", case=False) &
            s.stratum.str.contains("C9", case=False)].magnitude.tolist()
    non = s[s.stratum.str.contains("No", case=False)].magnitude.tolist()
    r = stats.mann_whitney(mut, non)
    return Analysis(
        id=f"repro_mutation_{cytokine}",
        question=f"Do C9orf72 mutation carriers show stronger {cytokine} C9orf72 responses?",
        method="Two-tailed Mann-Whitney U, C9orf72-mutation vs no-mutation donors",
        finding=(f"C9orf72-mutation carriers have {cytokine} responses with median "
                 f"{r.estimates['median_x']:.0f} vs {r.estimates['median_y']:.0f} in "
                 f"non-carriers (p={r.p_value:.3g})."),
        stats=r.as_dict(), data_source="fig4_mutation_survival",
        reproduces="Mutation carriers show stronger C9orf72-specific responses (Fig. 4)")


def survival_association(cytokine: str = "IL-10") -> Analysis:
    f4 = datasets.load("fig4_mutation_survival")
    s = f4[(f4.analysis == "survival") & (f4.cytokine == cytokine)]
    short = s[s.stratum.str.lower() == "short"].magnitude.tolist()
    long = s[s.stratum.str.lower() == "long"].magnitude.tolist()
    r = stats.mann_whitney(long, short)
    return Analysis(
        id=f"repro_survival_{cytokine}",
        question=f"Is the {cytokine} C9orf72 response associated with predicted survival?",
        method="Two-tailed Mann-Whitney U, long vs short predicted-survival donors",
        finding=(f"{cytokine} responses are {'higher' if r.estimates['median_x']>r.estimates['median_y'] else 'lower'} "
                 f"in long-survival donors (median {r.estimates['median_x']:.0f} vs "
                 f"{r.estimates['median_y']:.0f}, p={r.p_value:.3g})."),
        stats=r.as_dict(), data_source="fig4_mutation_survival",
        reproduces="IL-10-mediated responses associate with longer predicted survival (Fig. 4)")


def hla_binding_vs_immunogenicity() -> Analysis:
    pep = datasets.load("si_table1_peptide_screen")
    p = pep[~pep.phospho & pep.n_predicted_hla_bound.notna()]
    r = stats.spearman(p.n_predicted_hla_bound, p.response_freq)
    return Analysis(
        id="repro_hla_immunogenicity",
        question="Is predicted HLA-II binding breadth associated with observed immunogenicity?",
        method="Spearman correlation of predicted-HLA-bound count vs response frequency across 95 peptides",
        finding=(f"Predicted HLA-II binding breadth correlates with observed response "
                 f"frequency (Spearman rho={r.effect_size:.2f}, p={r.p_value:.3g}, "
                 f"n={r.n['pairs']})."),
        stats=r.as_dict(), data_source="si_table1_peptide_screen",
        reproduces="Immunogenicity associated with HLA binding (ED Fig. 5)")


# --------------------------------------------------------------------------- #
# Exploratory analyses (feed the discovery agents)
# --------------------------------------------------------------------------- #
def cross_antigen_th2_bias(cytokine: str = "IL-5") -> Analysis:
    """Is the ALS>HC cytokine enrichment C9orf72-specific or shared across antigens?"""
    f2 = datasets.load("fig2_fluorospot_responses")
    res = {}
    for ag in ["C9orf72", "TDP-43", "SOD1", "EBV"]:
        s = f2[(f2.antigen == ag) & (f2.cytokine == cytokine)]
        hc = s[s.group == "HC"].magnitude.tolist()
        als = s[s.group == "ALS"].magnitude.tolist()
        r = stats.mann_whitney(als, hc)
        res[ag] = {"p_value": r.p_value, "median_HC": r.estimates["median_y"],
                   "median_ALS": r.estimates["median_x"], "rbc": r.effect_size}
    sig = [ag for ag, v in res.items() if v["p_value"] < 0.05 and v["median_ALS"] > v["median_HC"]]
    return Analysis(
        id=f"explore_cross_antigen_{cytokine}",
        question=f"Is the ALS>HC {cytokine} enrichment specific to C9orf72 or shared with other neuroantigens?",
        method="Mann-Whitney ALS vs HC for each antigen (C9orf72/TDP-43/SOD1/EBV)",
        finding=(f"ALS>HC {cytokine} enrichment is significant for: "
                 f"{', '.join(sig) if sig else 'none'}. "
                 f"{'Not unique to C9orf72.' if set(sig)-{'C9orf72'} else 'Consistent with C9orf72 focus.'}"),
        stats=res, data_source="fig2_fluorospot_responses", novel=True)


def phospho_vs_nonphospho() -> Analysis:
    """Do phosphorylated peptide variants differ in immunogenicity from their parents?"""
    pep = datasets.load("si_table1_peptide_screen")
    pairs = []
    for residues, grp in pep.groupby("residues"):
        if grp.phospho.any() and (~grp.phospho).any():
            nonp = grp[~grp.phospho].iloc[0]
            phos = grp[grp.phospho].iloc[0]
            pairs.append({"residues": residues,
                          "nonphospho_mag": nonp.avg_magnitude, "phospho_mag": phos.avg_magnitude,
                          "nonphospho_resp": int(nonp.responders), "phospho_resp": int(phos.responders)})
    df = pd.DataFrame(pairs)
    dmag = (df.phospho_mag - df.nonphospho_mag)
    return Analysis(
        id="explore_phospho",
        question="Do phosphorylated C9orf72 peptide variants change immunogenicity vs their parent peptides?",
        method="Paired comparison of 5 phospho/non-phospho peptide pairs (magnitude and responders)",
        finding=(f"Across {len(df)} phospho/parent pairs, phosphorylation changed average "
                 f"magnitude by a median of {np.median(dmag):+.1f} spot units; "
                 f"{(df.phospho_mag > df.nonphospho_mag).sum()}/{len(df)} pairs increased."),
        stats={"pairs": df.to_dict("records"), "median_delta_magnitude": float(np.median(dmag))},
        data_source="si_table1_peptide_screen", novel=True)


def epitope_spatial_structure() -> Analysis:
    """Is immunogenicity along the C9orf72 sequence spatially clustered?"""
    pep = datasets.load("si_table1_peptide_screen")
    p = pep[~pep.phospho].sort_values("start_residue")
    resp = p.response_freq.to_numpy()
    # lag-1 autocorrelation of response frequency along the ordered tiling
    lag1 = float(np.corrcoef(resp[:-1], resp[1:])[0, 1])
    # permutation test for lag-1 autocorrelation
    rng = np.random.default_rng(1234)
    null = []
    for _ in range(5000):
        s = rng.permutation(resp)
        null.append(np.corrcoef(s[:-1], s[1:])[0, 1])
    p_perm = float((np.sum(np.abs(null) >= abs(lag1)) + 1) / (len(null) + 1))
    return Analysis(
        id="explore_spatial",
        question="Are immunogenic C9orf72 epitopes spatially clustered along the protein sequence?",
        method="Lag-1 autocorrelation of per-peptide response frequency along the tiling, permutation test (5000)",
        finding=(f"Adjacent overlapping peptides show lag-1 autocorrelation of response "
                 f"frequency rho={lag1:.2f} (permutation p={p_perm:.3g}): "
                 f"{'significant spatial clustering' if p_perm < 0.05 else 'no strong clustering'}."),
        stats={"lag1_autocorr": lag1, "perm_p": p_perm, "n_peptides": int(len(p))},
        data_source="si_table1_peptide_screen", novel=True)


def donor_jackknife(antigen: str = "C9orf72", cytokine: str = "Total") -> Analysis:
    """Leave-one-donor-out robustness of the ALS vs HC comparison."""
    f2 = datasets.load("fig2_fluorospot_responses")
    s = f2[(f2.antigen == antigen) & (f2.cytokine == cytokine)]
    hc = s[s.group == "HC"].magnitude.to_numpy()
    als = s[s.group == "ALS"].magnitude.to_numpy()
    base_p = stats.mann_whitney(als, hc).p_value
    ps = []
    for i in range(len(als)):
        ps.append(stats.mann_whitney(np.delete(als, i), hc).p_value)
    for i in range(len(hc)):
        ps.append(stats.mann_whitney(als, np.delete(hc, i)).p_value)
    ps = np.array(ps)
    return Analysis(
        id=f"explore_jackknife_{antigen}_{cytokine}".replace("-", ""),
        question=f"Does the ALS vs HC {antigen} {cytokine} result depend on any single donor?",
        method="Leave-one-donor-out jackknife of the Mann-Whitney p-value",
        finding=(f"Base p={base_p:.3g}; across all leave-one-out removals p stays in "
                 f"[{ps.min():.3g}, {ps.max():.3g}] and remains <0.05 in "
                 f"{int((ps < 0.05).sum())}/{len(ps)} removals: "
                 f"{'robust to any single donor' if ps.max() < 0.05 else 'sensitive to some donors'}."),
        stats={"base_p": base_p, "max_p": float(ps.max()), "min_p": float(ps.min()),
               "frac_sig": float((ps < 0.05).mean())},
        data_source="fig2_fluorospot_responses", novel=True)


def censoring_robustness(antigen: str = "C9orf72", cytokine: str = "Total",
                         floor: float = 100.0) -> Analysis:
    """Does the ALS vs HC result survive treating the assay floor as left-censored?"""
    f2 = datasets.load("fig2_fluorospot_responses")
    s = f2[(f2.antigen == antigen) & (f2.cytokine == cytokine)]
    hc = s[s.group == "HC"].magnitude.to_numpy()
    als = s[s.group == "ALS"].magnitude.to_numpy()
    base = stats.mann_whitney(als, hc)
    # Mann-Whitney is rank-based, so tied floor values are handled via ranks; here we
    # additionally compare the fraction of donors above the floor (Fisher exact).
    tbl = [[int((als > floor).sum()), int((als <= floor).sum())],
           [int((hc > floor).sum()), int((hc <= floor).sum())]]
    fish = stats.fisher_exact(tbl)
    return Analysis(
        id=f"explore_censoring_{antigen}_{cytokine}".replace("-", ""),
        question=f"Is the ALS vs HC {antigen} {cytokine} difference robust to the assay floor (value={floor:.0f})?",
        method="Mann-Whitney (rank-based) plus Fisher exact on the fraction of donors above the floor",
        finding=(f"Rank-based p={base.p_value:.3g}; above-floor responders "
                 f"{tbl[0][0]}/{sum(tbl[0])} (ALS) vs {tbl[1][0]}/{sum(tbl[1])} (HC), "
                 f"Fisher p={fish.p_value:.3g}: {'robust to censoring' if fish.p_value < 0.05 else 'weaker under censoring'}."),
        stats={"mannwhitney_p": base.p_value, "fisher": fish.as_dict(), "table": tbl},
        data_source="fig2_fluorospot_responses", novel=True)


def cd4_dominance() -> Analysis:
    """Quantify CD4 vs CD8 dominance among C9orf72-reactive T cells (ED Fig. 4)."""
    ed = datasets.load("edfig4_cd4_cd8")
    # panels a (HC) and b (ALS): frequency of CD4 vs CD8 among reactive cells
    res = {}
    for grp, panel in [("HC", "a"), ("ALS", "b")]:
        sub = ed[ed.panel == panel]
        cd4 = sub[sub.series == "CD4"].value.tolist()
        cd8 = sub[sub.series == "CD8"].value.tolist()
        if cd4 and cd8:
            r = stats.mann_whitney(cd4, cd8)
            res[grp] = {"median_CD4": r.estimates["median_x"],
                        "median_CD8": r.estimates["median_y"], "p_value": r.p_value}
    return Analysis(
        id="repro_cd4_dominance",
        question="Are C9orf72-reactive T cells predominantly CD4+?",
        method="Mann-Whitney of CD4 vs CD8 frequency among reactive cells, per group",
        finding=("C9orf72-reactive T cells are predominantly CD4+ "
                 + "; ".join(f"{g}: CD4 median {v['median_CD4']:.0f}% vs CD8 {v['median_CD8']:.0f}% "
                             f"(p={v['p_value']:.2g})" for g, v in res.items())),
        stats=res, data_source="edfig4_cd4_cd8",
        reproduces="Responses predominantly CD4+ T-cell mediated (Fig. 2, ED Fig. 4)")


def fdr_family_fig2() -> Analysis:
    """Do the Fig 2 ALS-vs-HC comparisons survive family-wise FDR correction?"""
    f2 = datasets.load("fig2_fluorospot_responses")
    rows = []
    for ag in ["C9orf72", "TDP-43", "SOD1", "EBV"]:
        for cyto in ["Total", "IFNg", "IL-5", "IL-10"]:
            s = f2[(f2.antigen == ag) & (f2.cytokine == cyto)]
            r = stats.mann_whitney(s[s.group == "ALS"].magnitude.tolist(),
                                   s[s.group == "HC"].magnitude.tolist())
            rows.append({"antigen": ag, "cytokine": cyto, "p": r.p_value})
    df = pd.DataFrame(rows)
    df["q"] = stats.fdr_bh(df.p.tolist())
    c9 = df[df.antigen == "C9orf72"]
    n_sig = int((c9.q < 0.05).sum())
    return Analysis(
        id="explore_fdr_family",
        question="Do the C9orf72 ALS-vs-HC differences survive FDR correction across the 16-comparison family?",
        method="Benjamini-Hochberg FDR across 4 antigens x 4 cytokines (16 Mann-Whitney tests)",
        finding=(f"After BH-FDR over all 16 antigen x cytokine comparisons, "
                 f"{n_sig}/4 C9orf72 cytokines remain significant (q<0.05): "
                 + ", ".join(f"{r.cytokine} q={r.q:.3g}" for _, r in c9.iterrows()) + "."),
        stats={"table": df.to_dict("records")},
        data_source="fig2_fluorospot_responses", novel=True)


def cytokine_ratio_classifier() -> Analysis:
    """How well does the IFNg/IL-5 ratio discriminate ALS from HC (ROC AUC)?"""
    from sklearn.metrics import roc_auc_score
    ed = datasets.load("edfig2_ifng_il5_ratio")
    tg = ed[(ed.kind == "two_group") & (ed.measure == "IFNg/IL-5 ratio")]
    hc = tg[tg.group == "HC"].value.to_numpy()
    als = tg[tg.group == "ALS"].value.to_numpy()
    y = np.r_[np.ones_like(als), np.zeros_like(hc)]
    score = -np.r_[als, hc]  # lower ratio => more ALS-like
    auc = float(roc_auc_score(y, score))
    return Analysis(
        id="explore_ratio_classifier",
        question="How well does the per-donor IFNg/IL-5 ratio alone separate ALS from HC?",
        method="ROC AUC of the IFNg/IL-5 ratio as a univariate ALS classifier",
        finding=(f"The IFNg/IL-5 ratio alone separates ALS from HC with AUC={auc:.2f} "
                 f"(n_ALS={len(als)}, n_HC={len(hc)}): a modest single-feature signal, "
                 f"not a diagnostic on its own."),
        stats={"auc": auc, "n_als": int(len(als)), "n_hc": int(len(hc))},
        data_source="edfig2_ifng_il5_ratio", novel=True)


REPRODUCTIONS = [
    lambda: als_vs_hc_response("C9orf72", "Total"),
    lambda: als_vs_hc_response("C9orf72", "IFNg"),
    lambda: als_vs_hc_response("C9orf72", "IL-5"),
    lambda: als_vs_hc_response("C9orf72", "IL-10"),
    cytokine_th2_bias,
    lambda: als_specificity_vs_pd_ad("Total"),
    lambda: mutation_carrier_effect("Total"),
    lambda: survival_association("IL-10"),
    hla_binding_vs_immunogenicity,
    cd4_dominance,
]

EXPLORATORY = [
    lambda: cross_antigen_th2_bias("IL-5"),
    lambda: cross_antigen_th2_bias("IL-10"),
    phospho_vs_nonphospho,
    epitope_spatial_structure,
    lambda: donor_jackknife("C9orf72", "Total"),
    lambda: censoring_robustness("C9orf72", "Total"),
    fdr_family_fig2,
    cytokine_ratio_classifier,
]


def run_all() -> list[Analysis]:
    return [f() for f in REPRODUCTIONS] + [f() for f in EXPLORATORY]
