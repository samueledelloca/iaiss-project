# Analysis results

## Reproductions of the paper's claims

- **repro_fig2_C9orf72_Total**: C9orf72 Total responses are higher in ALS (median 6720 vs 1142, p=0.00159, rank-biserial r=-0.49).  
  _reproduces:_ C9orf72-specific responses increased in ALS (Fig. 2)
- **repro_fig2_C9orf72_IFNg**: C9orf72 IFNg responses are higher in ALS (median 2185 vs 627, p=0.0381, rank-biserial r=-0.33).  
  _reproduces:_ C9orf72-specific responses increased in ALS (Fig. 2)
- **repro_fig2_C9orf72_IL5**: C9orf72 IL-5 responses are higher in ALS (median 2330 vs 208, p=0.000318, rank-biserial r=-0.56).  
  _reproduces:_ C9orf72-specific responses increased in ALS (Fig. 2)
- **repro_fig2_C9orf72_IL10**: C9orf72 IL-10 responses are higher in ALS (median 1029 vs 177, p=0.00469, rank-biserial r=-0.44).  
  _reproduces:_ C9orf72-specific responses increased in ALS (Fig. 2)
- **repro_th2_bias**: The IFNg/IL-5 ratio is lower in ALS (median 0.65) than HC (median 1.26), p=0.0483: an IL-5-biased response in ALS.  
  _reproduces:_ ALS responses enriched for IL-5/IL-10 over IFNg (Fig. 2, ED Fig. 2)
- **repro_specificity_Total**: ALS Total C9orf72 responses differ from ALS_vs_HC at p<0.05.  
  _reproduces:_ C9orf72 response relatively specific to ALS (ED Fig. 2)
- **repro_mutation_Total**: C9orf72-mutation carriers have Total responses with median 7263 vs 100 in non-carriers (p=0.0281).  
  _reproduces:_ Mutation carriers show stronger C9orf72-specific responses (Fig. 4)
- **repro_survival_IL-10**: IL-10 responses are higher in long-survival donors (median 1153 vs 100, p=0.0382).  
  _reproduces:_ IL-10-mediated responses associate with longer predicted survival (Fig. 4)
- **repro_hla_immunogenicity**: Predicted HLA-II binding breadth correlates with observed response frequency (Spearman rho=0.29, p=0.00385, n=95).  
  _reproduces:_ Immunogenicity associated with HLA binding (ED Fig. 5)
- **repro_cd4_dominance**: C9orf72-reactive T cells are predominantly CD4+ HC: CD4 median 83% vs CD8 9% (p=3.4e-06); ALS: CD4 median 92% vs CD8 5% (p=3.4e-06)  
  _reproduces:_ Responses predominantly CD4+ T-cell mediated (Fig. 2, ED Fig. 4)

## Exploratory analyses (candidate novel observations)

- **explore_cross_antigen_IL-5**: ALS>HC IL-5 enrichment is significant for: C9orf72, TDP-43. Not unique to C9orf72.
- **explore_cross_antigen_IL-10**: ALS>HC IL-10 enrichment is significant for: C9orf72. Consistent with C9orf72 focus.
- **explore_phospho**: Across 5 phospho/parent pairs, phosphorylation changed average magnitude by a median of +8.7 spot units; 3/5 pairs increased.
- **explore_spatial**: Adjacent overlapping peptides show lag-1 autocorrelation of response frequency rho=0.47 (permutation p=0.0002): significant spatial clustering.
- **explore_jackknife_C9orf72_Total**: Base p=0.00159; across all leave-one-out removals p stays in [0.000607, 0.00263] and remains <0.05 in 56/56 removals: robust to any single donor.
- **explore_censoring_C9orf72_Total**: Rank-based p=0.00159; above-floor responders 27/28 (ALS) vs 22/28 (HC), Fisher p=0.101: weaker under censoring.
- **explore_fdr_family**: After BH-FDR over all 16 antigen x cytokine comparisons, 3/4 C9orf72 cytokines remain significant (q<0.05): Total q=0.0127, IFNg q=0.122, IL-5 q=0.00508, IL-10 q=0.025.
- **explore_ratio_classifier**: The IFNg/IL-5 ratio alone separates ALS from HC with AUC=0.68 (n_ALS=26, n_HC=17): a modest single-feature signal, not a diagnostic on its own.
