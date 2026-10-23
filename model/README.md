# model/ — the C9orf72 Paper2Agent (MCP server)

`mcp_server.py` exposes the study's computational tools over the Model Context
Protocol, turning the Nature paper into an interactive, executable agent.

## Run

```bash
python model/mcp_server.py        # stdio transport
```

## Connect from Claude Code

The repo ships `.mcp.json`; from the repo root, Claude Code will offer to start
the `c9orf72-nature2agent` server. Then ask, e.g., *"reproduce the C9orf72 IL-5
ALS-vs-HC comparison"* or *"which epitopes have the broadest HLA-II coverage?"*.

## Tools (14)

| Tool | Purpose |
|---|---|
| `explain_experimental_design` | study design, cohorts, assays, statistics |
| `list_datasets` / `describe_dataset` / `query_dataset` | machine-readable data access |
| `epitope_table` / `most_immunogenic_epitopes` / `broadest_hla_coverage` | peptide/epitope interrogation |
| `hla_typing` | per-donor HLA typing |
| `reproduce_claim` / `run_analysis` / `list_analyses` | reproduce claims and run named analyses |
| `compare_groups` | generic two-tailed Mann-Whitney |
| `reported_pvalues` | the authors' own p-values (validation) |
| `protein_sequence` | C9orf72 sequence (UniProt Q96LT7) |

All tools are covered by `tests/test_tools.py` and `tests/test_mcp.py`.
