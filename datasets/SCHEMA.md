# Machine-readable datasets

Tidy CSVs derived from the Michaelis et al. (2025) Nature source data (CC-BY 4.0;
attribute to the original study). Regenerate with `python scripts/build_datasets.py`.
Provenance (input checksums, package versions) is in `datasets_manifest.json`.

Sources: Nature source-data workbook `MOESM3_ESM.xlsx` (per-figure values),
Supplementary Information PDF (Tables S1, S2), and the manuscript JATS tables.

| File | Source | Grain | Key columns |
|---|---|---|---|
| `fig2_fluorospot_responses.csv` | Fig 2a-d | one FluoroSpot value per donor | cytokine (Total/IFNg/IL-5/IL-10), antigen (TDP-43/SOD1/C9orf72/EBV), group (HC/ALS), donor_idx, magnitude |
| `fig1_tcell_subsets.csv` | Fig 1 | one % per donor | compartment, subset, group, donor_idx, percent |
| `fig3_epitopes.csv` | Fig 3 | one row per epitope (1-100) | epitope_num, pct_responded, avg_magnitude, responses_by_donor |
| `fig4_mutation_survival.csv` | Fig 4 | one value per donor | cytokine, stratum (mutation status / survival Short-Long), donor_idx, magnitude |
| `edfig2_ifng_il5_ratio.csv` | ED Fig 2 | one value per donor | measure, group (HC/ALS/PD/AD), donor_idx, value |
| `edfig4_cd4_cd8.csv` | ED Fig 4 | one value per donor | panel, sub, series, donor_idx, value |
| `edfig5_immunogenicity_hla.csv` | ED Fig 5 | mixed | panel, series, idx, value |
| `edfig6_clinical_correlates.csv` | ED Fig 6 | one value per donor | panel, measure, series (ALSFRS/C9ORF72/...), idx, value |
| `reported_pvalues.csv` | ED Fig 2 panel | one row per reported comparison | figure_legend, comparison, raw_p (authors' own values, for validation) |
| `si_table1_peptide_screen.csv` | SI Table S1 | one row per peptide (100) | epitope_num, residues, start_residue, sequence, phospho, responders, tested, response_freq, avg_magnitude, n_predicted_hla_bound |
| `si_table2_hla_typing.csv` | SI Table S2 | one row per donor×locus×allele | donor, locus, allele_index, allele (23 donors, HLA-I and HLA-II) |
| `table1_epitopes_ge3donors.csv` | Table 1 | epitopes recognised in >=3 ALS donors | Peptide residue, Peptide sequence, Response frequency (%), Average magnitude |
| `table2_hla_restrictions.csv` | Table 2 | HLA-restricted peptides | Peptide sequence, Allele, RATE P value, Binding percentile rank |

## Cross-validation performed at build time

- `fig3_epitopes` epitope #14 == SI `si_table1_peptide_screen` #14 == Table 1 row
  "56-70 DGEITFLANHTLNGE, 7/22 (32%), magnitude 1216" (the top epitope).
- Fig 2 C9orf72 medians increase HC->ALS for Total/IFNg/IL-5/IL-10, consistent with
  the paper's central claim.
- Epitope numbering (1-100) follows screen order **including** the 5 phospho variants.

## Notes

- FluoroSpot `magnitude` is in the assay's spot-based units; the floor value 100 is
  the assay minimum used by the authors.
- Assay N differs by figure (the FluoroSpot screen used ~28 donors per group, not the
  full 40 ALS / 28 HC cohort); counts are carried per dataset rather than assumed.
