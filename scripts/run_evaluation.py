#!/usr/bin/env python3
"""Run the common evaluation framework (scientific + AI) and persist results."""
from __future__ import annotations
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import config, evaluation, paths, provenance, seeds

def main() -> None:
    cfg = config.load_config(); seeds.set_global_seed(cfg["reproducibility"]["random_seed"])
    out = paths.EVALUATION; out.mkdir(parents=True, exist_ok=True)
    sci = evaluation.scientific_evaluation(); ai = evaluation.ai_evaluation()
    (out / "scientific.json").write_text(json.dumps(sci, indent=2, default=str))
    (out / "ai.json").write_text(json.dumps(ai, indent=2, default=str))
    provenance.write_manifest(out, provenance.capture_provenance(cfg, seed=cfg["reproducibility"]["random_seed"]))
    print("Scientific:",
          f"reproduced {sci['reproducibility']['paper_claims_reproduced']}/{sci['reproducibility']['n_reproduction_questions']} claims,",
          f"fidelity max|dp|={sci['reproducibility']['reported_pvalue_fidelity']['max_abs_diff']:.4f},",
          f"{sci['novelty']['verified_novel_observations']} novel observations")
    print("AI:",
          f"grounding={ai['hallucination']['grounding_rate']:.2f},",
          f"tool_acc={ai['tool_use_accuracy']['accuracy']:.2f},",
          f"deterministic={ai['reproducibility']['deterministic']},",
          f"nulls_rejected={ai['false_hypothesis_rejection']['correctly_rejected']}/{ai['false_hypothesis_rejection']['n']},",
          f"self_flagged={ai['self_error_detection']['questions_self_flagged']}")

if __name__ == "__main__":
    main()
