"""Raw FCS ingestion tests."""
from __future__ import annotations
import pytest
from c9n2a import flow, paths
pytestmark = pytest.mark.skipif(not flow.ICS_DIRS, reason="raw ICS FCS not fetched")

def test_index_covers_all_fcs_with_groups():
    df = flow.index_ics_fcs()
    assert len(df) >= 85
    assert set(df.group.unique()) >= {"ALS", "HC"}
    assert set(df.condition.unique()) >= {"Negative", "Peptide", "Positive"}
    assert df.n_events.min() > 1000

def test_channel_panel_has_markers():
    panel = flow.channel_panel()
    assert any("FSC" in c for c in panel)
