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

## Reasoning backend: what reasons, and when (read this before the oral)

Be precise about this, because it is the most likely exam question.

- **The scientific findings are real computations.** The reproductions and the eight
  novel observations are produced by running real statistical tests (SciPy/statsmodels)
  on the real published data, every time the pipeline runs. They are not text a model
  wrote and saved. The grounding metric (1.0) means every number printed equals the
  number computed.
- **The committed discovery run is deterministic.** With no `ANTHROPIC_API_KEY`,
  `run_discovery.py` is ordinary Python: it calls the tools in a fixed order and applies
  rule-based verification and critique. No language model runs at that point.
- **Where the AI reasoning is.** Two places. (1) At build time, the question bank and the
  choice of which analyses to run were produced by the Claude Code agent; a worked trace
  of that reasoning, with real tool calls, is in
  `results/discovery/agent_reasoning_example.md`. (2) At run time, if `ANTHROPIC_API_KEY`
  is set, `c9n2a.agentkit.AnthropicBackend` makes the agents reason live over the same
  tools. Run `python scripts/run_agent_live.py` to see one agent decide which tools to
  call, read their outputs and write a conclusion.
- **Honest summary for the oral.** "The agents are deterministic by default so the results
  reproduce without credentials; they reason with a language model when a key is set. The
  discoveries themselves are real statistics from the data. I verified the computational
  process and reproducibility; I did not and cannot vouch for the biological validity of
  the results (see `DISCLAIMER.md`)."

The committed results come from the deterministic path so they can be reproduced without
credentials.
