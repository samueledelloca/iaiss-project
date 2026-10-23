# agents/ - the agentic scientific ecosystem

Declarative specifications for the five-layer architecture. The runtime is
`src/c9n2a/agentkit.py`; the discovery loop is `src/c9n2a/discovery.py`.

Every agent run is logged under `experiments/agent_runs/`.


## Layer 3 - Scientific agents

- **literature_agent** (scientific) - Find external support/contradiction for findings. Tools: explain_experimental_design.
- **immunology_agent** (scientific) - Interpret cytokine responses and Th phenotype. Tools: list_datasets, describe_dataset, query_dataset, run_analysis, reproduce_claim, compare_groups, list_analyses.
- **als_agent** (scientific) - Relate findings to ALS biology, mutation status and controls. Tools: list_datasets, describe_dataset, query_dataset, run_analysis, reproduce_claim, compare_groups, list_analyses.
- **hla_agent** (scientific) - Analyse HLA typing, restriction and binding coverage. Tools: hla_typing, broadest_hla_coverage, run_analysis, query_dataset.
- **tcell_agent** (scientific) - Analyse CD4/CD8 and T-cell subset composition. Tools: list_datasets, describe_dataset, query_dataset, run_analysis, reproduce_claim, compare_groups, list_analyses.
- **drug_discovery_agent** (scientific) - Propose antigen-specific therapeutic strategies. Tools: most_immunogenic_epitopes, broadest_hla_coverage, run_analysis.
- **structural_agent** (scientific) - Analyse epitope sequence/position and modifications. Tools: protein_sequence, epitope_table, most_immunogenic_epitopes, run_analysis.
- **singlecell_agent** (scientific) - Propose single-cell follow-ups for phenotype identity. Tools: list_datasets, describe_dataset, query_dataset, run_analysis, reproduce_claim, compare_groups, list_analyses.
- **clinical_agent** (scientific) - Relate responses to survival and clinical variables. Tools: list_datasets, describe_dataset, query_dataset, run_analysis, reproduce_claim, compare_groups, list_analyses.
- **safety_agent** (scientific) - Stress-test robustness, multiple testing and censoring. Tools: run_analysis, reported_pvalues.

## Layer 4 - Discovery agents

- **hypothesis_generator** (discovery) - Generate testable questions from the data. Tools: list_analyses, list_datasets.
- **hypothesis_critic** (discovery) - Adversarially critique each hypothesis/answer. Tools: none.
- **evidence_checker** (discovery) - Independently recompute and verify each finding. Tools: run_analysis, reproduce_claim.
- **replication_agent** (discovery) - Re-run robustness checks (jackknife, FDR, censoring). Tools: run_analysis.
- **contradiction_agent** (discovery) - Classify each finding vs the paper's claims. Tools: reproduce_claim.
- **experiment_designer** (discovery) - Design the most efficient falsification experiment. Tools: most_immunogenic_epitopes, hla_typing.
- **falsification_agent** (discovery) - State what observation would falsify each claim. Tools: none.

## Layer 5 - Principal Investigator

- **pi_agent** (pi) - Integrate all outputs; cannot override contradictory evidence. Tools: list_analyses.

The PI agent integrates all outputs but cannot override contradictory experimental evidence.

