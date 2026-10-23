"""Peptide-immunogenicity predictor tests."""
from __future__ import annotations
import pytest
from c9n2a import paths, predictor
pytestmark = pytest.mark.skipif(
    not (paths.DATASETS / "si_table1_peptide_screen.csv").exists(),
    reason="datasets not built")

def test_features_shape_and_label():
    X, y = predictor.build_features(min_responders=3)
    assert len(X) == 95 and len(y) == 95
    assert set(y) <= {0, 1} and 0 < y.sum() < len(y)
    assert "n_predicted_hla_bound" in X.columns and "hydropathy" in X.columns

def test_train_returns_auc():
    _, res = predictor.train(seed=1234)
    assert res.n == 95
    assert 0.0 <= res.cv_auc_mean <= 1.0
    assert 0.0 <= res.baseline_auc_mean <= 1.0
    assert res.feature_importance
