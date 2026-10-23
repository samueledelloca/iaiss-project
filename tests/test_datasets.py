"""Tests validating the parsed datasets against known paper facts."""
from __future__ import annotations

import numpy as np
import pytest

from c9n2a import source_data as sd

pytestmark = pytest.mark.skipif(
    not sd.WORKBOOK.exists(), reason="raw source data not fetched")


def test_peptide_screen_has_100_peptides():
    pep = sd.parse_peptide_screen()
    assert len(pep) == 100
    assert pep["phospho"].sum() == 5
    top = pep[pep.epitope_num == 14].iloc[0]
    assert top["residues"] == "56-70"
    assert top["sequence"] == "DGEITFLANHTLNGE"
    assert top["responders"] == 7 and top["tested"] == 22
    assert abs(top["avg_magnitude"] - 1215.9) < 0.1


def test_hla_typing_covers_23_donors_and_classii():
    hla = sd.parse_hla_typing()
    assert hla["donor"].nunique() == 23
    assert {"HLA-DRB1", "HLA-DQB1", "HLA-DPB1"} <= set(hla["locus"].unique())
    # no malformed alleles
    bad = hla[hla.allele.notna() & ~hla.allele.str.contains(r"\*\d", na=False)]
    assert bad.empty


def test_fig2_c9orf72_increases_in_als():
    import openpyxl
    wb = openpyxl.load_workbook(sd.WORKBOOK, data_only=True)
    f2 = sd.build_fig2_fluorospot(wb)
    assert set(f2.cytokine.unique()) == {"Total", "IFNg", "IL-5", "IL-10"}
    assert set(f2.antigen.unique()) == {"TDP-43", "SOD1", "C9orf72", "EBV"}
    c9 = f2[f2.antigen == "C9orf72"]
    for cyto in ["Total", "IL-5", "IL-10"]:
        hc = c9[(c9.cytokine == cyto) & (c9.group == "HC")].magnitude
        als = c9[(c9.cytokine == cyto) & (c9.group == "ALS")].magnitude
        assert np.median(als) > np.median(hc)
