# C9orf72-Nature2Agent

An autonomous AI scientist built from the Michaelis et al. (2025) *Nature* study
on ALS autoimmunity. The system turns the paper, its supplementary material and
its source data into an interactive, executable agent that explains the design,
retrieves observations, reproduces the statistical analyses and figures,
interrogates the peptide and HLA data, tests alternative statistical assumptions,
generates new hypotheses and verifies them.

> IAISS 2026 Project 1. Primary reference: Michaelis et al., *Autoimmune response
> to C9orf72 protein in amyotrophic lateral sclerosis*, Nature (2025),
> [10.1038/s41586-025-09588-6](https://doi.org/10.1038/s41586-025-09588-6).
> Open access: PMC [PMC12657233](https://pmc.ncbi.nlm.nih.gov/articles/PMC12657233/).

## Scientific question

Can AI agents use the C9orf72 autoimmune mechanism to move from observation to
mechanism to hypothesis to a falsifiable therapeutic proposal? The system
reproduces the study's claims from its own data, then produces verified
observations that the paper does not state, and frames a patient-stratified,
antigen-specific therapeutic hypothesis with an explicit falsification experiment.

## What it does (headline results)

- **Reproduces every headline claim** from the real source data: C9orf72 responses
  increase in ALS (Total p=0.0016, IL-5 p=0.0003, IL-10 p=0.0047), an IL-5/IL-10
  bias over IFNγ, CD4 dominance (p=3e-6), stronger responses in mutation carriers,
  an IL-10/survival association, and an HLA-binding/immunogenicity correlation.
  Reproduced p-values match the authors' reported values to within 0.0013.
- **Eight verified novel observations** (success criterion is five), including:
  immunogenicity is spatially clustered along the protein sequence (permutation
  p=2e-4); the ALS IL-5 bias is shared with TDP-43 while the IL-10 bias is
  C9orf72-specific; the IFNγ increase does not survive family-wise FDR; the central
  result is robust to any single donor.
- **24 questions answered and independently re-verified**, a contradictions /
  uncertainties / limitations catalogue, and a scientific + AI evaluation.

## Architecture

```
Layer 1  Scientific knowledge  Nature paper + SI + source data + external literature (scite)
Layer 2  Paper agent           MCP server exposing the study as 15 validated tools
Layer 3  Scientific agents     literature, immunology, ALS, HLA, T-cell, drug-discovery,
                               structural, single-cell, clinical, safety
Layer 4  Discovery agents      hypothesis generator, critic, evidence checker, replication,
                               contradiction, experiment designer, falsification
Layer 5  PI agent              integrates outputs; cannot override contradictory evidence
```

The computational core is deterministic and reproducible. With no API key the
reasoning agents run in-session and their runs are logged; with `ANTHROPIC_API_KEY`
set the same agents run live over the same tools. See `agents/README.md`.

## Repository layout

| Path | Contents |
|---|---|
| `src/c9n2a/` | library: data IO, stats, analyses, figures, RAG, flow, tools, agent kit, discovery, evaluation |
| `model/` | the MCP server (Paper2Agent) |
| `agents/` | agent specifications (`registry.json`) and the architecture |
| `datasets/` | 14 machine-readable tidy tables + schema |
| `data/` | raw data fetchers + provenance (raw files are not committed) |
| `literature/` | RAG index, paper text, curated external references |
| `results/` | analyses, figures, discovery outputs |
| `evaluation/` | scientific + AI evaluation results |
| `reports/` | the 20-page PhD report (LaTeX) |
| `scripts/`, `tests/`, `configs/` | pipeline scripts, tests, configuration |

## Quickstart

```bash
./run.sh setup       # venv + pinned deps (Python 3.12)
./run.sh fetch       # Zenodo ICS data + PMC supplementary (MD5-verified)
./run.sh all         # datasets, analyses, figures, discovery, evaluation, tests
```

Individual stages: `datasets | analyses | figures | discovery | evaluate | test`.

### Use the agent (MCP)

```bash
./run.sh mcp         # start the Paper2Agent MCP server (stdio)
```

From the repo root an MCP client (Claude Code via `.mcp.json`, or Claude Desktop)
can connect and ask, for example, *"reproduce the C9orf72 IL-5 ALS-vs-HC comparison"*
or *"which epitopes have the broadest HLA-II coverage?"*.

## Deliverables map

| Brief deliverable | Where |
|---|---|
| C9orf72 Paper2Agent | `model/mcp_server.py`, `src/c9n2a/tools.py` |
| Reproducible environment | `requirements.txt`, `environment.yml`, `run.sh`, fixed seeds |
| Machine-readable datasets | `datasets/` (+ `SCHEMA.md`) |
| Automated reproduction of analyses + figures | `scripts/run_analyses.py`, `scripts/reproduce_figures.py` |
| 20+ new questions + answers | `results/discovery/questions.json` (24) |
| >=5 verified novel observations | `results/discovery/observations.json` (8) |
| Contradictions / uncertainties / limitations | `results/discovery/contradictions.json` |
| Scientific + AI evaluation | `evaluation/` |
| GitHub repository | this repo |
| 20-page report | `reports/` |

## Reproducibility

Fixed seeds (`configs/base.yaml`), pinned dependencies, per-run provenance
manifests (git commit, config hash, package versions, input checksums), versioned
data (Zenodo record id + per-file MD5), logged agent runs, and a deterministic
discovery loop. The AI tools used and all prompts/agent configurations are
documented in [`AI_USAGE.md`](AI_USAGE.md).

## Licensing

Code is MIT (`LICENSE`). The data are redistributed under their upstream licenses
(Zenodo deposits are CC-BY 4.0; PMC open-access article and supplementary); see
`data/DATA_SOURCES.md`. Attribute Michaelis et al. (2025) for any scientific use.
