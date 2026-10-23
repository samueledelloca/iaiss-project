#!/usr/bin/env python3
"""Run the agentic discovery loop and write all deliverables.

Writes:
  results/discovery/questions.json      - 24 questions, answers, verification, critique
  results/discovery/observations.json   - verified novel observations (>=5)
  results/discovery/contradictions.json - contradictions / uncertainties / limitations
  results/discovery/summary.md
  agents/registry.json                  - machine-readable agent specifications
  agents/README.md                      - the 5-layer architecture
Agent run logs are written under experiments/agent_runs/.

Usage:  python scripts/run_discovery.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from c9n2a import config, discovery, paths, provenance, seeds  # noqa: E402


def export_agents() -> None:
    specs = [{"name": s.name, "layer": s.layer, "kind": s.kind, "role": s.role,
              "tools": s.tools, "system_prompt": s.system_prompt}
             for s in discovery.AGENT_SPECS.values()]
    (paths.AGENTS / "registry.json").write_text(json.dumps(specs, indent=2))
    by_layer = {}
    for s in specs:
        by_layer.setdefault(s["layer"], []).append(s)
    lines = ["# agents/ - the agentic scientific ecosystem\n",
             "Declarative specifications for the five-layer architecture. The runtime is\n"
             "`src/c9n2a/agentkit.py`; the discovery loop is `src/c9n2a/discovery.py`.\n",
             "Every agent run is logged under `experiments/agent_runs/`.\n"]
    names = {3: "Layer 3 - Scientific agents", 4: "Layer 4 - Discovery agents",
             5: "Layer 5 - Principal Investigator"}
    for layer in sorted(by_layer):
        lines.append(f"\n## {names.get(layer, f'Layer {layer}')}\n")
        for s in by_layer[layer]:
            lines.append(f"- **{s['name']}** ({s['kind']}) - {s['role']} "
                         f"Tools: {', '.join(s['tools']) or 'none'}.")
    lines.append("\nThe PI agent integrates all outputs but cannot override contradictory "
                 "experimental evidence.\n")
    (paths.AGENTS / "README.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    cfg = config.load_config()
    seeds.set_global_seed(cfg["reproducibility"]["random_seed"])
    out = paths.RESULTS / "discovery"
    out.mkdir(parents=True, exist_ok=True)

    res = discovery.orchestrate(backend=cfg["agents"]["backend"])
    (out / "questions.json").write_text(json.dumps(res["questions"], indent=2, default=str))
    (out / "observations.json").write_text(json.dumps(res["observations"], indent=2, default=str))
    (out / "contradictions.json").write_text(json.dumps(res["contradictions"], indent=2, default=str))
    export_agents()

    nq = len(res["questions"]); nv = sum(a["verified"] for a in res["questions"])
    lines = [f"# Discovery results\n",
             f"{nq} questions answered; {nv} computationally verified; "
             f"{len(res['observations'])} verified novel observations.\n",
             "## Verified novel observations\n"]
    for o in res["observations"]:
        lines.append(f"- **{o['id']}** [{o['status']}] {o['observation']}")
    lines.append("\n## Questions and answers\n")
    for a in res["questions"]:
        flags = f" _(flags: {'; '.join(a['critique_flags'])})_" if a["critique_flags"] else ""
        lines.append(f"- **{a['id']}** ({a['kind']}, {a['owner']}): {a['question']}  \n"
                     f"  → {a['answer'] if isinstance(a['answer'], str) else '[structured result]'} "
                     f"[{a['relation_to_paper']}; verified={a['verified']}]{flags}")
    lines.append("\n## Contradictions, uncertainties and limitations\n")
    for c in res["contradictions"]:
        lines.append(f"- **{c['id']}** ({c['type']}): {c['item']}")
    (out / "summary.md").write_text("\n".join(lines) + "\n")

    provenance.write_manifest(out, provenance.capture_provenance(
        cfg, seed=cfg["reproducibility"]["random_seed"]))
    print(f"Discovery complete: {nq} questions, {nv} verified, "
          f"{len(res['observations'])} novel observations, "
          f"{len(res['contradictions'])} catalogue items. See {out}")


if __name__ == "__main__":
    main()
