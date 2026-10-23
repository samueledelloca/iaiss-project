# Citation audit

Every external reference in the report was checked in two ways: its bibliographic
metadata against the Crossref record (authors, year, venue, volume, pages, DOI),
and its content against the specific sentence it supports (abstract at minimum,
full-text excerpts for ambiguous cases) via the scite literature tools. Editorial
notices were checked; none of the cited works is retracted.

## Metadata corrections (Crossref-verified)

The literature was first gathered by topic and labelled with a first-author guess;
Crossref correction fixed three misattributed first authors and added volume and
pages to every entry:

| Key | Was | Correct first author (Crossref) | Record |
|---|---|---|---|
| `appel2012` | Appel | **Henkel, Jenny S.** (2012) | EMBO Mol Med 5, 64-79 |
| `appel2020` | Appel | **Zhao, Weihua** (2020) | iScience 23, 101192 |
| `al2024` | Al | **Bender, Christine** (2024) | Sci Transl Med 16, eadn2404 |
| `michaelis2025c9orf72` | Michaelis | **Michaelis, Tanner** (2025) | Nature 647, 970-978 |

## Content corrections (source checked against the claim)

Four references supported a related but narrower claim than the sentence first
attached to them. Each was re-scoped to what its source actually states:

- **komiya2020** is an ALS *model* (SOD1-G93A mouse) study of CCR2+ monocyte
  infiltration and microglia. The report no longer implies human tissue; it is
  cited for microglia and infiltrating monocytes in ALS model tissue.
- **appel2020 (Zhao)** shows regulatory T-cell *dysfunction* in ALS, not the
  number-versus-progression link. It is cited for Treg dysfunction only.
- **rajabinejad2019** is a systematic review supporting Treg-directed *therapy*
  (survival extension in models), not a patient-level reduction. It is cited for
  the therapeutic rationale only.
- The regulatory T-cell *number and function fall with faster progression* claim
  is now cited only to **appel2012 (Henkel)**, which states it directly
  ("numbers of Tregs and their FoxP3 ... were reduced in rapidly progressing ALS
  patients and inversely correlated with progression rates").

The NetMHCIIpan binding-prediction method citation (`nielsen2008`, `jensen2018`)
was moved next to the binding predictor, away from the RATE restriction method.

## Result

Of 14 external references: all metadata Crossref-verified; content verified against
the source for each; 0 contradicted the claim; 0 retracted (one erratum noted on
Henkel 2012, which is not a retraction). Four over-attributions were corrected as
above. One contrasting reference (Bender 2024, a negative polyclonal-Treg trial) is
kept deliberately to avoid an over-optimistic therapeutic reading.
