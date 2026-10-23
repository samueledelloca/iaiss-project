# Data sources and provenance

All primary data come from Michaelis et al., *Autoimmune response to C9orf72
protein in amyotrophic lateral sclerosis*, Nature (2025),
DOI [10.1038/s41586-025-09588-6](https://doi.org/10.1038/s41586-025-09588-6).
Open-access full text and supplementary tables: PMC **PMC12657233** (PMID 41034581).

Raw data are **not committed to git** (size + CC-BY redistribution hygiene). They
are fetched and MD5-verified by `scripts/fetch_data.py`, which writes a
`provenance.json` per record. Only small derived, machine-readable tables under
`datasets/` are committed, each with attribution.

## Zenodo deposits (raw flow cytometry; CC-BY 4.0)

| Record | DOI | Content | Size | Files |
|---|---|---|---|---|
| [16749283](https://zenodo.org/records/16749283) | 10.5281/zenodo.16749283 | Spectral data (immunophenotyping FCS) | 1641 MB | 44 |
| [16749334](https://zenodo.org/records/16749334) | 10.5281/zenodo.16749334 | ICS data Screen 1 | 152 MB | 26 |
| [16754553](https://zenodo.org/records/16754553) | 10.5281/zenodo.16754553 | ICS data Screen 2 | 45 MB | 19 |
| [16754591](https://zenodo.org/records/16754591) | 10.5281/zenodo.16754591 | ICS data Screen 3 | 58 MB | 26 |
| [16754609](https://zenodo.org/records/16754609) | 10.5281/zenodo.16754609 | ICS data Screen 4 | 139 MB | 26 |

Each ICS screen contains `.fcs` files named `{ALS|HC} Specimen_... {Negative|Peptide|Positive}.fcs`
(intracellular cytokine staining after restimulation with the C9orf72 peptide
pool; Negative = unstimulated background, Positive = polyclonal control) plus
FlowJo `.wsp` workspace(s) encoding the gating strategy.

## Nature / PMC supplementary (open access)

| File | Content |
|---|---|
| `41586_2025_9588_MOESM3_ESM.xlsx` | Supplementary Tables (peptide list, HLA typing, per-donor responses, survival) |
| `41586_2025_9588_MOESM1_ESM.pdf` | Supplementary Information (methods, extended data) |
| `PMC12657233.jats.xml` | Full-text JATS XML (main tables + text, for the RAG corpus) |

Fetched via EuropePMC / E-utilities into `data/raw/pmc/` and `data/raw/supplementary/`.

## Licensing

- Zenodo deposits: **CC-BY 4.0** (attribution to Michaelis et al. 2025 required; carried in each `provenance.json` and in derived dataset headers).
- PMC open-access article + supplementary: per the article's open-access license.
- This repository's **code** is MIT (see `LICENSE`); redistributed/derived **data** retain their upstream licenses and are attributed accordingly.

## Reproduce

```bash
python scripts/fetch_data.py --records ics    # four ICS screens (~394 MB)
python scripts/fetch_data.py --records all    # add spectral data (~2.0 GB total)
```
