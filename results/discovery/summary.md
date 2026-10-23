# Discovery results

24 questions answered; 24 computationally verified; 8 verified novel observations.

## Verified novel observations

- **Q13** [verified] ALS>HC IL-5 enrichment is significant for: C9orf72, TDP-43. Not unique to C9orf72.
- **Q14** [verified] ALS>HC IL-10 enrichment is significant for: C9orf72. Consistent with C9orf72 focus.
- **Q15** [verified] Across 5 phospho/parent pairs, phosphorylation changed average magnitude by a median of +8.7 spot units; 3/5 pairs increased.
- **Q16** [verified] Adjacent overlapping peptides show lag-1 autocorrelation of response frequency rho=0.47 (permutation p=0.0002): significant spatial clustering.
- **Q17** [verified] Base p=0.00159; across all leave-one-out removals p stays in [0.000607, 0.00263] and remains <0.05 in 56/56 removals: robust to any single donor.
- **Q18** [verified] Rank-based p=0.00159; above-floor responders 27/28 (ALS) vs 22/28 (HC), Fisher p=0.101: weaker under censoring.
- **Q19** [verified] After BH-FDR over all 16 antigen x cytokine comparisons, 3/4 C9orf72 cytokines remain significant (q<0.05): Total q=0.0127, IFNg q=0.122, IL-5 q=0.00508, IL-10 q=0.025.
- **Q20** [verified] The IFNg/IL-5 ratio alone separates ALS from HC with AUC=0.68 (n_ALS=26, n_HC=17): a modest single-feature signal, not a diagnostic on its own.

## Questions and answers

- **Q01** (reproduction, immunology_agent): Are C9orf72 total FluoroSpot responses increased in ALS vs HC?  
  → C9orf72 Total responses are higher in ALS (median 6720 vs 1142, p=0.00159, rank-biserial r=-0.49). [agrees; verified=True]
- **Q02** (reproduction, immunology_agent): Are C9orf72 IL-5 responses increased in ALS vs HC?  
  → C9orf72 IL-5 responses are higher in ALS (median 2330 vs 208, p=0.000318, rank-biserial r=-0.56). [agrees; verified=True]
- **Q03** (reproduction, immunology_agent): Are C9orf72 IL-10 responses increased in ALS vs HC?  
  → C9orf72 IL-10 responses are higher in ALS (median 1029 vs 177, p=0.00469, rank-biserial r=-0.44). [agrees; verified=True]
- **Q04** (reproduction, immunology_agent): Are C9orf72 IFNg responses increased in ALS vs HC?  
  → C9orf72 IFNg responses are higher in ALS (median 2185 vs 627, p=0.0381, rank-biserial r=-0.33). [agrees; verified=True] _(flags: marginal significance (0.01<=p<0.05); multiple-testing sensitive)_
- **Q05** (reproduction, immunology_agent): Do ALS responses show an IL-5/IL-10 bias over IFNg?  
  → The IFNg/IL-5 ratio is lower in ALS (median 0.65) than HC (median 1.26), p=0.0483: an IL-5-biased response in ALS. [agrees; verified=True] _(flags: marginal significance (0.01<=p<0.05); multiple-testing sensitive)_
- **Q06** (reproduction, tcell_agent): Are C9orf72-reactive T cells predominantly CD4+?  
  → C9orf72-reactive T cells are predominantly CD4+ HC: CD4 median 83% vs CD8 9% (p=3.4e-06); ALS: CD4 median 92% vs CD8 5% (p=3.4e-06) [agrees; verified=True]
- **Q07** (reproduction, als_agent): Is the ALS C9orf72 response specific vs PD and AD controls?  
  → ALS Total C9orf72 responses differ from HC (p<0.05) and not from PD, AD: elevated versus healthy controls but not statistically distinguished from the other neurodegenerative groups. [agrees; verified=True]
- **Q08** (reproduction, als_agent): Do C9orf72-mutation carriers show stronger responses?  
  → C9orf72-mutation carriers have Total responses with median 7263 vs 100 in non-carriers (p=0.0281). [agrees; verified=True] _(flags: small sample (n<15 in a group); marginal significance (0.01<=p<0.05); multiple-testing sensitive)_
- **Q09** (reproduction, clinical_agent): Is the IL-10 C9orf72 response associated with predicted survival?  
  → IL-10 responses are higher in long-survival donors (median 1153 vs 100, p=0.0382). [agrees; verified=True] _(flags: small sample (n<15 in a group); marginal significance (0.01<=p<0.05); multiple-testing sensitive)_
- **Q10** (reproduction, hla_agent): Is predicted HLA-II binding associated with observed immunogenicity?  
  → Predicted HLA-II binding breadth correlates with observed response frequency (Spearman rho=0.29, p=0.00385, n=95). [agrees; verified=True]
- **Q11** (extension, hla_agent): Which C9orf72 epitopes have the broadest predicted HLA-II coverage?  
  → [structured result] [neutral; verified=True]
- **Q12** (extension, structural_agent): Which C9orf72 epitopes are most broadly immunogenic?  
  → [structured result] [neutral; verified=True]
- **Q13** (novel, immunology_agent): Is the ALS IL-5 bias specific to C9orf72 or shared across neuroantigens?  
  → ALS>HC IL-5 enrichment is significant for: C9orf72, TDP-43. Not unique to C9orf72. [caveats (extends: the IL-5 ALS bias is not unique to C9orf72); verified=True]
- **Q14** (novel, immunology_agent): Is the ALS IL-10 bias specific to C9orf72 or shared across neuroantigens?  
  → ALS>HC IL-10 enrichment is significant for: C9orf72. Consistent with C9orf72 focus. [extends (new observation consistent with the paper's framework); verified=True]
- **Q15** (novel, structural_agent): Do phosphorylated peptide variants change immunogenicity?  
  → Across 5 phospho/parent pairs, phosphorylation changed average magnitude by a median of +8.7 spot units; 3/5 pairs increased. [extends (new observation consistent with the paper's framework); verified=True] _(flags: only 5 phospho/parent pairs; underpowered)_
- **Q16** (novel, structural_agent): Is epitope immunogenicity spatially clustered along the sequence?  
  → Adjacent overlapping peptides show lag-1 autocorrelation of response frequency rho=0.47 (permutation p=0.0002): significant spatial clustering. [extends (new observation consistent with the paper's framework); verified=True]
- **Q17** (novel, safety_agent): Does the central ALS-vs-HC result depend on any single donor?  
  → Base p=0.00159; across all leave-one-out removals p stays in [0.000607, 0.00263] and remains <0.05 in 56/56 removals: robust to any single donor. [extends (new observation consistent with the paper's framework); verified=True]
- **Q18** (novel, safety_agent): Is the ALS-vs-HC difference robust to the assay floor (censoring)?  
  → Rank-based p=0.00159; above-floor responders 27/28 (ALS) vs 22/28 (HC), Fisher p=0.101: weaker under censoring. [caveats (robustness limitation under censoring / multiple testing); verified=True]
- **Q19** (novel, safety_agent): Do the C9orf72 differences survive family-wise FDR correction?  
  → After BH-FDR over all 16 antigen x cytokine comparisons, 3/4 C9orf72 cytokines remain significant (q<0.05): Total q=0.0127, IFNg q=0.122, IL-5 q=0.00508, IL-10 q=0.025. [caveats (robustness limitation under censoring / multiple testing); verified=True]
- **Q20** (novel, clinical_agent): How well does the IFNg/IL-5 ratio alone separate ALS from HC?  
  → The IFNg/IL-5 ratio alone separates ALS from HC with AUC=0.68 (n_ALS=26, n_HC=17): a modest single-feature signal, not a diagnostic on its own. [extends (new observation consistent with the paper's framework); verified=True] _(flags: single-feature AUC is modest; not a diagnostic)_
- **Q21** (interpretive, drug_discovery_agent): What antigen-specific therapeutic strategy does the mechanism suggest?  
  → [structured result] [neutral; verified=True] _(flags: hypothesis, not a validated therapy; requires falsification experiment)_
- **Q22** (interpretive, experiment_designer): What experiment would most efficiently falsify the core hypothesis?  
  → [structured result] [neutral; verified=True] _(flags: hypothesis, not a validated therapy; requires falsification experiment)_
- **Q23** (interpretive, singlecell_agent): What single-cell follow-up would resolve the CD4 phenotype identity?  
  → [structured result] [neutral; verified=True] _(flags: hypothesis, not a validated therapy; requires falsification experiment)_
- **Q24** (interpretive, literature_agent): Is the C9orf72 autoimmunity finding supported by external literature?  
  → [structured result] [neutral; verified=True] _(flags: hypothesis, not a validated therapy; requires falsification experiment)_

## Contradictions, uncertainties and limitations

- **Q13** (caveats (extends: the IL-5 ALS bias is not unique to C9orf72)): ALS>HC IL-5 enrichment is significant for: C9orf72, TDP-43. Not unique to C9orf72.
- **Q18** (caveats (robustness limitation under censoring / multiple testing)): Rank-based p=0.00159; above-floor responders 27/28 (ALS) vs 22/28 (HC), Fisher p=0.101: weaker under censoring.
- **Q19** (caveats (robustness limitation under censoring / multiple testing)): After BH-FDR over all 16 antigen x cytokine comparisons, 3/4 C9orf72 cytokines remain significant (q<0.05): Total q=0.0127, IFNg q=0.122, IL-5 q=0.00508, IL-10 q=0.025.
- **L1** (limitation): FluoroSpot magnitude is in assay-specific spot units with a floor of 100; the ALS>HC total-response difference weakens when reduced to the fraction of above-floor responders (Fisher p=0.10).
- **L2** (limitation): The C9orf72 IFNg ALS>HC increase does not survive BH-FDR across the 16-comparison family (q=0.12), unlike IL-5/IL-10/Total.
- **L3** (uncertainty): Survival and mutation strata have small per-group n; effects are consistent with the paper but individually marginal.
