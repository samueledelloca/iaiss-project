# AI usage and documentation

This project was built with AI as an active component of the scientific workflow,
as the IAISS brief requires. The student inspected and tested all AI-assisted code
(37 automated tests) and remains scientifically responsible for every output.

## AI systems used, mapped to the required roles

| Required role | System used | Where |
|---|---|---|
| Generative AI system | Claude (Opus 4.8) via Claude Code | this repository's code and report |
| Autonomous / semi-autonomous agent | Claude Code (build) + the in-repo discovery loop | `src/c9n2a/discovery.py` |
| Scientific literature agent | scite MCP (search + Smart Citations) | `literature/citations.json`, Literature agent |
| Computational biology / bioinformatics agent | the tool server (stats, epitope, HLA, raw FCS) + IEDB NetMHCIIpan-4.1 EL (authors' predictions, methods-faithful) | `src/c9n2a/tools.py`, `flow.py` |
| Independent verification agent | evidence checker + replication agent + evaluation grounding/determinism checks | `discovery.py`, `evaluation.py` |
| Adversarial / critical-review agent | hypothesis critic + falsification agent + false-hypothesis-rejection test | `discovery.py`, `evaluation.py` |

Supporting tools: the `research-companion` and `academic-writing-agents` Claude Code
plugins (hypothesis brainstorming and report drafting/review), `fastembed` ONNX
embeddings (scientific RAG), and the `mcp` SDK (the Paper2Agent server).

## Where the required documentation lives

The brief requires recording hypotheses, the evidence for and against, which were
rejected, which were tested, the prompts/agent specifications, and the AI-generated
code. In this repository:

1. **Every major hypothesis / question**: `results/discovery/questions.json` (24).
2. **Evidence supporting it**: the computed `stats` and `finding` per question,
   and `literature/citations.json` for external support.
3. **Evidence against it**: `critique_flags` per question and
   `results/discovery/contradictions.json` (limitations, uncertainties, caveats).
4. **Rejected hypotheses**: the planted nulls in the false-hypothesis-rejection
   test (`evaluation.false_hypothesis_test`), both correctly rejected.
5. **Hypotheses tested**: every non-interpretive question is computed and
   independently re-verified (`verified` field); robustness in
   `evaluation/scientific.json`.
6. **Prompts and agent specifications**: `agents/registry.json` (system prompts
   and tool permissions for all 18 agents); backend and model in
   `configs/base.yaml`; per-run logs under `experiments/agent_runs/`.
7. **AI-generated code**: the entire `src/c9n2a/` library, `model/`, `scripts/`
   and `tests/`, written with Claude Code, inspected and covered by tests.

## Reasoning backend and reproducibility

With no API key present, the reasoning agents run deterministically (the findings
are generated from computed statistics, so the hallucination rate is zero by
construction and the discovery loop is bit-for-bit reproducible). With
`ANTHROPIC_API_KEY` set, the same agents can run live over the same validated
tools (`c9n2a.agentkit.AnthropicBackend`). The committed results come from the
deterministic path so they can be reproduced without credentials.
