# Agent reasoning traces (example)

This file records the **reasoning** behind three discovery results, performed by the
Claude Code in-session agent (the project's reasoning backend when no
`ANTHROPIC_API_KEY` is set). Every tool call below is a real call to the MCP tools
in `src/c9n2a/tools.py`, and the numbers are the tools' real outputs. The committed
`run_discovery.py` then recomputes these same results deterministically.

> How this relates to the backends. With no API key, the generative and critical
> steps are done by this in-session agent and recorded (here and as the curated
> question bank), and `run_discovery.py` recomputes the answers from the tools. With
> `ANTHROPIC_API_KEY` set, `c9n2a.agentkit.AnthropicBackend` runs the same kind of
> tool-use reasoning live (see `scripts/run_agent_live.py`). The scientific findings
> are real statistics from the data either way; what the language layer contributes
> is the choice of what to ask and how to read the result.

---

## Trace 1 — Hypothesis Generator and Structural Agent: spatial structure

**Hypothesis.** The paper maps individual C9orf72 epitopes but does not say whether
immunogenic peptides are scattered or clustered along the protein. If recognition is
driven by a few antigenic regions, adjacent overlapping peptides should have
correlated response frequencies.

**Tool call.** `most_immunogenic_epitopes(top=6)` returns the strongest epitopes:
#14 (56-70, 7/22), #76 (366-380, 6/20), #89/#91 (426-445), #19 (81-95), #82 (396-410).
Reading the residue positions, the strongest hits fall in a small number of windows
(around 56-95 and around 366-445), which is the pattern clustering would predict.

**Tool call.** `run_analysis("explore_spatial")` computes the lag-1 autocorrelation of
response frequency along the ordered tiling with a 5000-shuffle permutation null:
*rho = 0.47, permutation p = 0.0002*.

**Interpretation.** The positive, significant autocorrelation supports the hypothesis:
immunogenicity occurs in contiguous stretches, consistent with a few antigenic regions
each spanning several overlapping 15-mers. This is a structural observation the paper
does not state.

**Adversarial critique (Hypothesis Critic).** Overlapping 15-mers share up to 10
residues, so some autocorrelation is expected from sequence overlap alone. The
permutation test controls for the marginal distribution of response values but not for
the overlap structure, so the effect size should be read as "more clustered than a
random relabelling", not as independent evidence of discrete epitopes. Verdict:
**keep, with the overlap caveat recorded.**

---

## Trace 2 — Immunology Agent and Critic: is the IL-5 bias C9orf72-specific?

**Hypothesis.** The study frames the IL-5 and IL-10 skew around C9orf72. If the IL-5
skew is a general ALS T-helper-2 phenomenon, it should also appear for the other
neuroantigens, not only C9orf72.

**Tool call.** `run_analysis("explore_cross_antigen_IL-5")` tests ALS-vs-HC IL-5 for
each antigen: the ALS increase is significant for **C9orf72 and TDP-43**, so the IL-5
skew is **not unique to C9orf72**. The companion `explore_cross_antigen_IL-10` finds the
IL-10 increase significant only for C9orf72.

**Interpretation.** The two cytokines behave differently. A shared IL-5 response points
to a general Th2 skew in ALS, while the IL-10 response, the component that tracks
survival, is antigen-specific to C9orf72. This sharpens the paper's framing and matters
for any intervention aimed at the protective arm.

**Adversarial critique (Critic).** TDP-43 significance could reflect cross-reactive or
bystander responses, and the per-antigen tests are not corrected as a family here. The
claim is therefore stated as "the IL-5 skew is shared", a weaker and defensible form,
and the FDR family test (Trace 3) is run on the C9orf72 comparisons. Verdict: **keep.**

---

## Trace 3 — Safety Agent and Falsification Agent: does the signal survive correction?

**Hypothesis.** The paper reports raw p-values for the C9orf72 ALS-vs-HC comparisons. A
sceptic would ask whether they survive correction across the whole family of
antigen-by-cytokine tests.

**Tool call.** `run_analysis("explore_fdr_family")` applies Benjamini-Hochberg across all
16 antigen x cytokine comparisons. For C9orf72: **Total q=0.013, IL-5 q=0.005,
IL-10 q=0.025 all survive; IFNg q=0.12 does not.**

**Interpretation.** The headline total, IL-5 and IL-10 increases are robust to multiple
testing, which strengthens the paper. The IFNg increase does not survive, so it should
be reported as suggestive at most. This is a limitation the system surfaces about the
original framing.

**Falsification.** The claim "C9orf72 responses are broadly elevated in ALS" would be
weakened if, under correction, none of the cytokines survived. Three of four do, so the
claim stands for Total, IL-5 and IL-10 and is withdrawn for IFNg. Verdict: **keep, with
IFNg demoted and catalogued as a limitation.**

---

Produced by the Claude Code in-session agent on the committed datasets. Reproduce the
underlying numbers with `python -m c9n2a.tools` calls or `./run.sh discovery`.
