"""Statistical primitives matching the paper's methods.

The study used GraphPad Prism's two-tailed Mann-Whitney test, one-way ANOVA with
Dunnett's multiple-comparison test, two-tailed Fisher exact test and Spearman's r.
These functions reproduce those tests with SciPy/statsmodels and add effect sizes
and bootstrap confidence intervals, so analyses can be both reproduced and
independently stress-tested.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import stats


@dataclass
class TestResult:
    test: str
    statistic: float
    p_value: float
    effect_size: float | None = None
    effect_name: str | None = None
    n: dict[str, int] = field(default_factory=dict)
    estimates: dict[str, float] = field(default_factory=dict)
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "test": self.test, "statistic": self.statistic, "p_value": self.p_value,
            "effect_size": self.effect_size, "effect_name": self.effect_name,
            "n": self.n, "estimates": self.estimates, **self.extra,
        }


def _clean(*arrays) -> tuple[np.ndarray, ...]:
    return tuple(np.asarray([v for v in a if v is not None and np.isfinite(v)],
                            dtype=float) for a in arrays)


def mann_whitney(x, y, alternative: str = "two-sided") -> TestResult:
    """Two-tailed Mann-Whitney U with rank-biserial effect size and medians."""
    x, y = _clean(x, y)
    u, p = stats.mannwhitneyu(x, y, alternative=alternative)
    # rank-biserial correlation = 1 - 2U2/(n1 n2); use U for x vs y
    rbc = 1 - (2 * u) / (len(x) * len(y))
    return TestResult(
        test="Mann-Whitney U (two-sided)", statistic=float(u), p_value=float(p),
        effect_size=float(rbc), effect_name="rank-biserial r",
        n={"x": len(x), "y": len(y)},
        estimates={"median_x": float(np.median(x)), "median_y": float(np.median(y)),
                   "median_diff": float(np.median(x) - np.median(y))},
    )


def fisher_exact(table, alternative: str = "two-sided") -> TestResult:
    """Two-tailed Fisher exact test on a 2x2 contingency table."""
    odds, p = stats.fisher_exact(table, alternative=alternative)
    return TestResult(test="Fisher exact (two-sided)", statistic=float(odds),
                      p_value=float(p), effect_size=float(odds),
                      effect_name="odds ratio", extra={"table": np.asarray(table).tolist()})


def spearman(x, y) -> TestResult:
    """Spearman rank correlation."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    rho, p = stats.spearmanr(x[mask], y[mask])
    return TestResult(test="Spearman r", statistic=float(rho), p_value=float(p),
                      effect_size=float(rho), effect_name="Spearman rho",
                      n={"pairs": int(mask.sum())})


def anova_dunnett(control, *treatments, labels=None) -> dict:
    """One-way ANOVA + Dunnett's test of each treatment vs the control group."""
    control = np.asarray(control, dtype=float)
    treatments = [np.asarray(t, dtype=float) for t in treatments]
    f, p_anova = stats.f_oneway(control, *treatments)
    dunnett = stats.dunnett(*treatments, control=control)
    labels = labels or [f"group{i+1}" for i in range(len(treatments))]
    return {
        "anova": {"F": float(f), "p_value": float(p_anova)},
        "dunnett": [{"group": labels[i], "statistic": float(dunnett.statistic[i]),
                     "p_value": float(dunnett.pvalue[i])} for i in range(len(treatments))],
    }


def bootstrap_ci(x, func=np.median, n_boot: int = 2000, alpha: float = 0.05,
                 seed: int = 1234) -> tuple[float, float, float]:
    """Percentile bootstrap CI for a statistic of one sample."""
    x = np.asarray([v for v in x if v is not None and np.isfinite(v)], dtype=float)
    rng = np.random.default_rng(seed)
    boots = np.array([func(rng.choice(x, size=len(x), replace=True))
                      for _ in range(n_boot)])
    lo, hi = np.quantile(boots, [alpha / 2, 1 - alpha / 2])
    return float(func(x)), float(lo), float(hi)


def fdr_bh(pvalues) -> np.ndarray:
    """Benjamini-Hochberg FDR-adjusted p-values."""
    from statsmodels.stats.multitest import multipletests
    return multipletests(pvalues, method="fdr_bh")[1]
