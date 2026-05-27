"""
test_live_evidence.py — Unit tests for the live evidence adapter.
"""
import pytest
from pathlib import Path
from datetime import datetime, timezone, timedelta

from tools.live_evidence_adapter import LiveEvidenceAdapter, LiveEvidenceBundle
from agent.schemas import EvidenceSourceLabel, EvidenceMode

_EXAMPLE_PATH = Path(__file__).parent.parent / "data" / "live_evidence_snapshot.example.json"


def test_evidence_source_labels_are_defined():
    """Ensure all required labels are present in the enum."""
    assert EvidenceSourceLabel.LIVE_BLOOMREACH_MCP.value == "LIVE BLOOMREACH MCP"
    assert EvidenceSourceLabel.MCP_SNAPSHOT.value == "MCP SNAPSHOT"
    assert EvidenceSourceLabel.SYNTHETIC_COMMERCE_OPS.value == "SYNTHETIC COMMERCE OPS"
    assert EvidenceSourceLabel.MOCK_FIXTURE.value == "MOCK FIXTURE"


def test_evidence_modes_are_defined():
    """Ensure all modes are present."""
    assert EvidenceMode.DEMO.value == "demo"
    assert EvidenceMode.SNAPSHOT.value == "snapshot"
    assert EvidenceMode.LIVE.value == "live"


def test_load_returns_none_when_snapshot_missing(tmp_path):
    """Adapter gracefully handles missing file."""
    missing_path = tmp_path / "does_not_exist.json"
    result = LiveEvidenceAdapter.load(missing_path)
    assert result is None


def test_load_returns_none_when_snapshot_invalid(tmp_path):
    """Adapter gracefully handles malformed JSON."""
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{ this is not json }")
    result = LiveEvidenceAdapter.load(invalid_path)
    assert result is None


def test_load_returns_bundle_when_valid_example_snapshot_present():
    """Adapter loads the schema correctly."""
    assert _EXAMPLE_PATH.exists(), "Example snapshot is missing"
    
    bundle = LiveEvidenceAdapter.load(_EXAMPLE_PATH)
    assert bundle is not None
    assert isinstance(bundle, LiveEvidenceBundle)
    assert bundle.project_display_name == "zesty-mongoose"
    assert bundle.funnel_overall is not None
    assert bundle.funnel_overall.sessions == 744
    assert len(bundle.checkout_trend) == 2


def test_snapshot_age_is_computed():
    """Age is calculated based on fetched_at."""
    # Create a bundle fetched 10 minutes ago
    ten_mins_ago = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    bundle = LiveEvidenceBundle(
        fetched_at=ten_mins_ago,
        project_display_name="test"
    )
    
    # Age should be ~10 minutes
    assert 9.9 < bundle.snapshot_age_minutes < 10.1


def test_snapshot_age_handles_invalid_date():
    """Invalid date string falls back to 9999."""
    bundle = LiveEvidenceBundle(
        fetched_at="not-a-date",
        project_display_name="test"
    )
    assert bundle.snapshot_age_minutes == 9999.0


def test_to_analytics_signals_uses_source_label():
    """Conversion to AnalyticsSignal attaches the correct label."""
    bundle = LiveEvidenceAdapter.load(_EXAMPLE_PATH)
    assert bundle is not None
    
    # Default label is MCP_SNAPSHOT
    signals = bundle.to_analytics_signals()
    assert len(signals) == 3
    for sig in signals:
        assert sig.source_label == EvidenceSourceLabel.MCP_SNAPSHOT.value
        
    # We can override the label to LIVE
    signals_live = bundle.to_analytics_signals(label=EvidenceSourceLabel.LIVE_BLOOMREACH_MCP)
    for sig in signals_live:
        assert sig.source_label == EvidenceSourceLabel.LIVE_BLOOMREACH_MCP.value
