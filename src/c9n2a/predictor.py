"""A small, reproducible peptide-immunogenicity predictor.

Predicts whether a C9orf72 peptide is immunogenic (recognised by at least three
donors, the threshold the paper uses for its epitope table) from predicted HLA-II
binding breadth and simple biochemical sequence features. The model is a
cross-validated gradient-boosting classifier with a logistic-regression baseline.
The sample is small (95 peptides), so the result is reported honestly as a weak
predictor rather than a tool for decisions.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from . import datasets

# Kyte-Doolittle hydropathy
_KD = {"A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
       "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
       "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2}
_AROMATIC = set("FWY")
_POS = set("KRH")
_NEG = set("DE")


def _seq_features(seq: str) -> dict:
    s = seq.replace("*", "")
    n = max(len(s), 1)
    return {
        "hydropathy": float(np.mean([_KD.get(a, 0) for a in s])),
        "aromatic_frac": sum(a in _AROMATIC for a in s) / n,
        "pos_frac": sum(a in _POS for a in s) / n,
        "neg_frac": sum(a in _NEG for a in s) / n,
        "net_charge": sum(a in _POS for a in s) - sum(a in _NEG for a in s),
    }


def build_features(min_responders: int = 3) -> tuple[pd.DataFrame, np.ndarray]:
    pep = datasets.load("si_table1_peptide_screen")
    pep = pep[~pep.phospho & pep.n_predicted_hla_bound.notna()].copy()
    feats = pep.sequence.apply(lambda s: pd.Series(_seq_features(s)))
    X = pd.concat([pep[["n_predicted_hla_bound", "start_residue"]].reset_index(drop=True),
                   feats.reset_index(drop=True)], axis=1)
    y = (pep.responders >= min_responders).astype(int).to_numpy()
    return X, y


@dataclass
class TrainResult:
    cv_auc_mean: float
    cv_auc_std: float
    baseline_auc_mean: float
    n: int
    n_positive: int
    feature_importance: dict


def train(seed: int = 1234, folds: int = 5) -> tuple[object, TrainResult]:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = build_features()
    k = min(folds, int(y.sum()), int((1 - y).sum()))
    gb = GradientBoostingClassifier(random_state=seed)
    base = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    auc = cross_val_score(gb, X, y, cv=k, scoring="roc_auc")
    base_auc = cross_val_score(base, X, y, cv=k, scoring="roc_auc")
    gb.fit(X, y)
    imp = dict(sorted(zip(X.columns, gb.feature_importances_),
                      key=lambda kv: -kv[1]))
    res = TrainResult(cv_auc_mean=float(auc.mean()), cv_auc_std=float(auc.std()),
                      baseline_auc_mean=float(base_auc.mean()), n=len(y),
                      n_positive=int(y.sum()),
                      feature_importance={k: float(v) for k, v in imp.items()})
    return gb, res
