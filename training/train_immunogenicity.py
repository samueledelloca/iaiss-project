#!/usr/bin/env python3
"""Train and checkpoint the peptide-immunogenicity predictor.

Writes the model to model/checkpoints/ and metrics to results/model/.
Usage:  python training/train_immunogenicity.py
"""
from __future__ import annotations
import json, pickle, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import config, paths, predictor, provenance, seeds

def main() -> None:
    cfg = config.load_config(); seed = cfg["reproducibility"]["random_seed"]
    seeds.set_global_seed(seed)
    model, res = predictor.train(seed=seed)
    ckpt_dir = paths.MODEL / "checkpoints"; ckpt_dir.mkdir(parents=True, exist_ok=True)
    with open(ckpt_dir / "immunogenicity_gb.pkl", "wb") as fh:
        pickle.dump(model, fh)
    out = paths.RESULTS / "model"; out.mkdir(parents=True, exist_ok=True)
    metrics = {**res.__dict__}
    (out / "immunogenicity_metrics.json").write_text(json.dumps(metrics, indent=2))
    provenance.write_manifest(out, provenance.capture_provenance(cfg, seed=seed))
    print(f"Trained on {res.n} peptides ({res.n_positive} immunogenic). "
          f"GB CV AUC={res.cv_auc_mean:.3f}+/-{res.cv_auc_std:.3f}, "
          f"logistic baseline AUC={res.baseline_auc_mean:.3f}.")
    print("Top features:", list(res.feature_importance)[:3])

if __name__ == "__main__":
    main()
