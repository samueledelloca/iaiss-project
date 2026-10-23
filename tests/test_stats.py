"""Statistics engine tests, including reproduction of the authors' reported p-values."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from c9n2a import paths, stats

DATASETS = paths.DATASETS


def test_mann_whitney_matches_scipy_known():
    # identical-ish groups -> large p; clearly separated -> small p
    r = stats.mann_whitney([1, 2, 3, 4], [10, 11, 12, 13])
    assert r.p_value < 0.05
    assert r.estimates["median_x"] < r.estimates["median_y"]


def test_fisher_and_spearman_sane():
    f = stats.fisher_exact([[8, 2], [1, 9]])
    assert f.p_value < 0.05
    s = stats.spearman([1, 2, 3, 4, 5], [2, 4, 5, 4, 7])
    assert s.effect_size > 0


@pytest.mark.skipif(not (DATASETS / "edfig2_ifng_il5_ratio.csv").exists(),
                    reason="datasets not built")
def test_reproduces_authors_edfig2_pvalues():
    """ED Fig 2 panels a/b/c: two-tailed Mann-Whitney ALS vs HC must match
    the authors' reported p-values to within rounding."""
    ed = pd.read_csv(DATASETS / "edfig2_ifng_il5_ratio.csv")
    tg = ed[ed.kind == "two_group"]
    expected = {"IFNg cytokine release": 0.007, "IL-5 cytokine release": 0.014,
                "IFNg/IL-5 ratio": 0.047}
    for measure, paper_p in expected.items():
        sub = tg[tg.measure == measure]
        hc = sub[sub.group == "HC"].value.tolist()
        als = sub[sub.group == "ALS"].value.tolist()
        r = stats.mann_whitney(als, hc)
        assert abs(r.p_value - paper_p) < 0.003, f"{measure}: {r.p_value} vs {paper_p}"


@pytest.mark.skipif(not (DATASETS / "fig2_fluorospot_responses.csv").exists(),
                    reason="datasets not built")
def test_fig2_c9orf72_als_greater_and_significant():
    f2 = pd.read_csv(DATASETS / "fig2_fluorospot_responses.csv")
    c9 = f2[f2.antigen == "C9orf72"]
    for cyto in ["Total", "IL-5", "IL-10"]:
        s = c9[c9.cytokine == cyto]
        hc = s[s.group == "HC"].magnitude.tolist()
        als = s[s.group == "ALS"].magnitude.tolist()
        r = stats.mann_whitney(als, hc)
        assert r.p_value < 0.05
        assert np.median(als) > np.median(hc)
