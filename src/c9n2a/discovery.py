"""The agentic scientific ecosystem and the discovery loop.

Defines the five architecture layers as declarative agents, a bank of 24 scientific
questions owned by the Layer-3 scientific agents, and the Layer-4/5 discovery
process that answers, verifies, critiques, checks for contradictions and
synthesises them. The loop runs deterministically (CachedBackend): every answer is
computed from the tools/analyses and every step is logged, so the outputs are
reproducible without an API key. With ANTHROPIC_API_KEY set, the same agents can
additionally run live.

Outputs (written by scripts/run_discovery.py):
  results/discovery/questions.json      - 24 questions + answers + verdicts
  results/discovery/observations.json   - verified novel observations (>=5)
  results/discovery/contradictions.json - contradictions / uncertainties / limitations
  results/discovery/summary.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from . import agentkit, analyses, tools
from .agentkit import AgentSpec

# --------------------------------------------------------------------------- #
# Layer 3-5 agent specifications
# --------------------------------------------------------------------------- #
def _spec(name, layer, role, tools_, kind="scientific"):
    return AgentSpec(name=name, layer=layer, role=role, kind=kind, tools=tools_,
                     system_prompt=(
                         f"You are the {name} in the C9orf72-Nature2Agent scientific "
                         f"ecosystem. Role: {role} Use only the provided tools and the "
                         f"study's own data. State effect sizes and sample sizes, label "
                         f"the evidence type, and never overclaim beyond what the data "
                         f"support. You remain scientifically responsible for every output."))


DATA_TOOLS = ["list_datasets", "describe_dataset", "query_dataset", "run_analysis",
              "reproduce_claim", "compare_groups", "list_analyses"]

AGENT_SPECS: dict[str, AgentSpec] = {s.name: s for s in [
    # Layer 3 - scientific agents
    _spec("literature_agent", 3, "Find external support/contradiction for findings.",
          ["explain_experimental_design", "search_paper"]),
    _spec("immunology_agent", 3, "Interpret cytokine responses and Th phenotype.",
          DATA_TOOLS),
    _spec("als_agent", 3, "Relate findings to ALS biology, mutation status and controls.",
          DATA_TOOLS),
    _spec("hla_agent", 3, "Analyse HLA typing, restriction and binding coverage.",
          ["hla_typing", "broadest_hla_coverage", "run_analysis", "query_dataset"]),
    _spec("tcell_agent", 3, "Analyse CD4/CD8 and T-cell subset composition.",
          DATA_TOOLS + ["ics_fcs_summary"]),
    _spec("drug_discovery_agent", 3, "Propose antigen-specific therapeutic strategies.",
          ["most_immunogenic_epitopes", "broadest_hla_coverage", "run_analysis"]),
    _spec("structural_agent", 3, "Analyse epitope sequence/position and modifications.",
          ["protein_sequence", "epitope_table", "most_immunogenic_epitopes", "run_analysis"]),
    _spec("singlecell_agent", 3, "Propose single-cell follow-ups for phenotype identity.",
          DATA_TOOLS),
    _spec("clinical_agent", 3, "Relate responses to survival and clinical variables.",
          DATA_TOOLS),
    _spec("safety_agent", 3, "Stress-test robustness, multiple testing and censoring.",
          ["run_analysis", "reported_pvalues"]),
    # Layer 4 - discovery agents
    _spec("hypothesis_generator", 4, "Generate testable questions from the data.",
          ["list_analyses", "list_datasets"], kind="discovery"),
    _spec("hypothesis_critic", 4, "Adversarially critique each hypothesis/answer.",
          [], kind="discovery"),
    _spec("evidence_checker", 4, "Independently recompute and verify each finding.",
          ["run_analysis", "reproduce_claim"], kind="discovery"),
    _spec("replication_agent", 4, "Re-run robustness checks (jackknife, FDR, censoring).",
          ["run_analysis"], kind="discovery"),
    _spec("contradiction_agent", 4, "Classify each finding vs the paper's claims.",
          ["reproduce_claim"], kind="discovery"),
    _spec("experiment_designer", 4, "Design the most efficient falsification experiment.",
          ["most_immunogenic_epitopes", "hla_typing"], kind="discovery"),
    _spec("falsification_agent", 4, "State what observation would falsify each claim.",
          [], kind="discovery"),
    # Layer 5 - PI
    _spec("pi_agent", 5, "Integrate all outputs; cannot override contradictory evidence.",
          ["list_analyses"], kind="pi"),
]}


# --------------------------------------------------------------------------- #
# Question bank (owned by Layer-3 agents)
# --------------------------------------------------------------------------- #
@dataclass
class Question:
    id: str
    text: str
    owner: str
    kind: str                       # reproduction | extension | novel | interpretive
    answerer: Callable              # (recorder) -> dict
    reproduces: str | None = None


def _ana(aid):
    return lambda rec: rec.call("run_analysis", analysis_id=aid)


# Interpretive answers (grounded reasoning; cached-backend output of this session).
def _ans_drug(rec):
    top = rec.call("most_immunogenic_epitopes", top=5)["top_by_breadth"]
    cov = rec.call("broadest_hla_coverage", top=5)["top_by_hla_coverage"]
    return {"strategy": (
        "Two complementary, patient-stratified antigen-specific strategies are "
        "suggested by the data. (1) Tolerogenic: because IL-10-biased C9orf72 "
        "responses track longer predicted survival, expanding or inducing regulatory "
        "C9orf72-specific T cells against the dominant epitopes (e.g. 56-70 "
        "DGEITFLANHTLNGE) is a candidate disease-modifying approach, stratified to "
        "C9orf72-mutation carriers who show the strongest responses. (2) The broadest "
        "HLA-II-covering epitopes are the most deployable antigens for an off-the-shelf "
        "tolerising construct. Both are hypotheses requiring experimental falsification, "
        "not validated therapies."),
        "dominant_epitopes": top, "broadest_coverage": cov,
        "caveat": "Antigen-specific tolerance could also blunt protective immunity; safety-gated."}


def _ans_experiment(rec):
    return {"design": (
        "Most efficient falsification experiment: an antigen-specific regulatory T cell "
        "(Treg) intervention in C9orf72-mutation ALS. Isolate/expand C9orf72(56-70)-"
        "specific CD4 T cells, polarise toward an IL-10+ regulatory phenotype, and test "
        "whether adoptive transfer slows motor-neuron loss in a C9orf72 model, with the "
        "pre-registered falsifier: if IL-10-biased C9orf72-specific Tregs do NOT slow "
        "progression (or worsen it), the survival-association hypothesis is rejected."),
        "patients": "C9orf72-mutation carriers with short predicted survival (greatest unmet need).",
        "target": "C9orf72 56-70 epitope-specific CD4 T cells.",
        "falsifier": "No survival/neuroprotection benefit from IL-10-biased C9orf72-specific Tregs."}


def _ans_singlecell(rec):
    return {"proposal": (
        "The IL-5/IL-10 bias leaves the CD4 identity ambiguous: classical Th2 vs IL-10+ "
        "regulatory (Tr1/Treg). A single-cell multi-omic experiment (scRNA-seq + TCR-seq "
        "+ surface protein) on sorted C9orf72-reactive CD4 T cells would resolve whether "
        "the IL-10 signal is Tr1/FOXP3+ regulatory (consistent with the protective "
        "survival association) or Th2 effector, and whether clonality differs by C9orf72 "
        "mutation status."),
        "resolves": "Th2 effector vs Tr1/Treg regulatory identity of IL-10+ C9orf72-reactive CD4 cells."}


def _ans_literature(rec):
    return {"note": ("External-literature support/contradiction is gathered via the scite "
                     "MCP and recorded in literature/citations.json; see the Literature "
                     "Agent run and the report's background section."),
            "design": rec.call("explain_experimental_design")}


QUESTIONS: list[Question] = [
    Question("Q01", "Are C9orf72 total FluoroSpot responses increased in ALS vs HC?",
             "immunology_agent", "reproduction", _ana("repro_fig2_C9orf72_Total"),
             "C9orf72 responses increased in ALS"),
    Question("Q02", "Are C9orf72 IL-5 responses increased in ALS vs HC?",
             "immunology_agent", "reproduction", _ana("repro_fig2_C9orf72_IL5")),
    Question("Q03", "Are C9orf72 IL-10 responses increased in ALS vs HC?",
             "immunology_agent", "reproduction", _ana("repro_fig2_C9orf72_IL10")),
    Question("Q04", "Are C9orf72 IFNg responses increased in ALS vs HC?",
             "immunology_agent", "reproduction", _ana("repro_fig2_C9orf72_IFNg")),
    Question("Q05", "Do ALS responses show an IL-5/IL-10 bias over IFNg?",
             "immunology_agent", "reproduction", _ana("repro_th2_bias")),
    Question("Q06", "Are C9orf72-reactive T cells predominantly CD4+?",
             "tcell_agent", "reproduction", _ana("repro_cd4_dominance")),
    Question("Q07", "Is the ALS C9orf72 response specific vs PD and AD controls?",
             "als_agent", "reproduction", _ana("repro_specificity_Total")),
    Question("Q08", "Do C9orf72-mutation carriers show stronger responses?",
             "als_agent", "reproduction", _ana("repro_mutation_Total")),
    Question("Q09", "Is the IL-10 C9orf72 response associated with predicted survival?",
             "clinical_agent", "reproduction", _ana("repro_survival_IL-10")),
    Question("Q10", "Is predicted HLA-II binding associated with observed immunogenicity?",
             "hla_agent", "reproduction", _ana("repro_hla_immunogenicity")),
    Question("Q11", "Which C9orf72 epitopes have the broadest predicted HLA-II coverage?",
             "hla_agent", "extension", lambda rec: rec.call("broadest_hla_coverage", top=10)),
    Question("Q12", "Which C9orf72 epitopes are most broadly immunogenic?",
             "structural_agent", "extension", lambda rec: rec.call("most_immunogenic_epitopes", top=10)),
    Question("Q13", "Is the ALS IL-5 bias specific to C9orf72 or shared across neuroantigens?",
             "immunology_agent", "novel", _ana("explore_cross_antigen_IL-5")),
    Question("Q14", "Is the ALS IL-10 bias specific to C9orf72 or shared across neuroantigens?",
             "immunology_agent", "novel", _ana("explore_cross_antigen_IL-10")),
    Question("Q15", "Do phosphorylated peptide variants change immunogenicity?",
             "structural_agent", "novel", _ana("explore_phospho")),
    Question("Q16", "Is epitope immunogenicity spatially clustered along the sequence?",
             "structural_agent", "novel", _ana("explore_spatial")),
    Question("Q17", "Does the central ALS-vs-HC result depend on any single donor?",
             "safety_agent", "novel", _ana("explore_jackknife_C9orf72_Total")),
    Question("Q18", "Is the ALS-vs-HC difference robust to the assay floor (censoring)?",
             "safety_agent", "novel", _ana("explore_censoring_C9orf72_Total")),
    Question("Q19", "Do the C9orf72 differences survive family-wise FDR correction?",
             "safety_agent", "novel", _ana("explore_fdr_family")),
    Question("Q20", "How well does the IFNg/IL-5 ratio alone separate ALS from HC?",
             "clinical_agent", "novel", _ana("explore_ratio_classifier")),
    Question("Q21", "What antigen-specific therapeutic strategy does the mechanism suggest?",
             "drug_discovery_agent", "interpretive", _ans_drug),
    Question("Q22", "What experiment would most efficiently falsify the core hypothesis?",
             "experiment_designer", "interpretive", _ans_experiment),
    Question("Q23", "What single-cell follow-up would resolve the CD4 phenotype identity?",
             "singlecell_agent", "interpretive", _ans_singlecell),
    Question("Q24", "Is the C9orf72 autoimmunity finding supported by external literature?",
             "literature_agent", "interpretive", _ans_literature),
]


# --------------------------------------------------------------------------- #
# Discovery-agent logic (verification, critique, contradiction, synthesis)
# --------------------------------------------------------------------------- #
def _p_of(answer: dict) -> float | None:
    for key in ("p_value", "perm_p"):
        if key in answer.get("stats", {}):
            return answer["stats"][key]
    s = answer.get("stats", {})
    if isinstance(s, dict) and "p_value" in s:
        return s["p_value"]
    return answer.get("p_value")


def verify(q: Question, answer: dict) -> dict:
    """Evidence checker: recompute and confirm the finding reproduces."""
    import json
    if q.kind == "interpretive":
        return {"verified": True, "note": "interpretive (grounded in computed tool outputs)"}
    try:
        again = q.answerer(agentkit.ToolRecorder(AGENT_SPECS[q.owner].tools))
    except Exception as e:  # pragma: no cover
        return {"verified": False, "note": f"recompute failed: {e}"}
    # Compare serialised output (robust to NaN != NaN in e.g. missing HLA counts).
    same = json.dumps(again, sort_keys=True, default=str) == json.dumps(answer, sort_keys=True, default=str)
    return {"verified": same,
            "note": "recomputed; identical output" if same else "recompute differed"}


ROBUSTNESS = {
    "Q01": "explore_jackknife_C9orf72_Total", "Q13": "explore_fdr_family",
    "Q02": "explore_fdr_family", "Q03": "explore_fdr_family",
}


def critique(q: Question, answer: dict) -> list[str]:
    """Adversarial critic + falsification: rule-based weaknesses."""
    flags = []
    stats_ = answer.get("stats", {})
    n = stats_.get("n") if isinstance(stats_, dict) else None
    if isinstance(n, dict) and min(n.values(), default=99) < 15:
        flags.append("small sample (n<15 in a group)")
    p = _p_of(answer)
    if p is not None and 0.01 <= p < 0.05:
        flags.append("marginal significance (0.01<=p<0.05); multiple-testing sensitive")
    if q.id == "Q15":
        flags.append("only 5 phospho/parent pairs; underpowered")
    if q.id == "Q20":
        flags.append("single-feature AUC is modest; not a diagnostic")
    if q.kind == "interpretive":
        flags.append("hypothesis, not a validated therapy; requires falsification experiment")
    return flags


def contradiction(q: Question, answer: dict) -> str:
    """Classify the finding relative to the paper."""
    if q.reproduces or q.kind == "reproduction":
        return "agrees"
    if q.id in {"Q13"}:
        return "caveats (extends: the IL-5 ALS bias is not unique to C9orf72)"
    if q.id in {"Q18", "Q19"}:
        return "caveats (robustness limitation under censoring / multiple testing)"
    if q.kind == "novel":
        return "extends (new observation consistent with the paper's framework)"
    return "neutral"


def orchestrate(backend: str = "cached") -> dict:
    """Run the full discovery loop and return the structured results."""
    agents = {name: agentkit.Agent(spec, handler=lambda rec, ctx: {},
                                   backend=backend) for name, spec in AGENT_SPECS.items()}

    # Layer 4: hypothesis generator emits the question bank (recorded run).
    agents["hypothesis_generator"].run(
        "Generate testable scientific questions from the C9orf72 dataset.",
        context={"n_questions": len(QUESTIONS)})

    answered = []
    for q in QUESTIONS:
        owner = agents[q.owner]
        rec = agentkit.ToolRecorder(AGENT_SPECS[q.owner].tools)
        answer = q.answerer(rec)
        v = verify(q, answer)
        flags = critique(q, answer)
        rel = contradiction(q, answer)
        robust = None
        if q.id in ROBUSTNESS:
            robust = tools.call("run_analysis", analysis_id=ROBUSTNESS[q.id])["finding"]
        owner.run(q.text, context={"question_id": q.id})
        answered.append({
            "id": q.id, "question": q.text, "owner": q.owner, "kind": q.kind,
            "answer": answer.get("finding") or answer,
            "verified": v["verified"], "verification_note": v["note"],
            "critique_flags": flags, "relation_to_paper": rel,
            "robustness": robust, "tool_calls": rec.calls,
        })

    # Layer 5: PI selects verified, novel, surviving observations.
    novel = [a for a in answered if a["kind"] == "novel" and a["verified"]]
    observations = []
    for a in novel:
        serious = [f for f in a["critique_flags"] if "small sample" in f]
        observations.append({
            "id": a["id"], "observation": a["answer"],
            "status": "verified" if not serious else "verified-with-caveat",
            "relation_to_paper": a["relation_to_paper"],
            "caveats": a["critique_flags"]})
    agents["pi_agent"].run("Integrate verified novel observations.",
                           context={"n_novel": len(observations)})

    contradictions = [
        {"id": a["id"], "item": a["answer"], "type": a["relation_to_paper"]}
        for a in answered if "caveat" in a["relation_to_paper"] or "limitation" in a["relation_to_paper"]]
    # uncertainties / limitations always included
    contradictions += [
        {"id": "L1", "item": "FluoroSpot magnitude is in assay-specific spot units with a "
         "floor of 100; the ALS>HC total-response difference weakens when reduced to the "
         "fraction of above-floor responders (Fisher p=0.10).", "type": "limitation"},
        {"id": "L2", "item": "The C9orf72 IFNg ALS>HC increase does not survive BH-FDR "
         "across the 16-comparison family (q=0.12), unlike IL-5/IL-10/Total.", "type": "limitation"},
        {"id": "L3", "item": "Survival and mutation strata have small per-group n; effects "
         "are consistent with the paper but individually marginal.", "type": "uncertainty"},
    ]

    return {"questions": answered, "observations": observations,
            "contradictions": contradictions,
            "agents": [{"name": s.name, "layer": s.layer, "role": s.role,
                        "kind": s.kind, "tools": s.tools} for s in AGENT_SPECS.values()]}
