import pytest
from unittest.mock import patch
from agent.orchestrator import Orchestrator
from agent.schemas import EvidenceMode
from tools.live_evidence_adapter import LiveEvidenceBundle

def test_default_demo_mode_returns_quebec_demo():
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.DEMO)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    assert brief.affected_region == "Quebec"
    assert any(t.status.value == "CALLED (MOCK)" for t in brief.tool_trace)
    assert any("SYNTHETIC OPS ADAPTER" in str(t.adapter).upper() for t in brief.tool_trace)
    assert brief.human_review_required is True
    assert brief.simulated_actions_only is True

def test_live_mode_with_bundle_uses_live_analytics():
    bundle = LiveEvidenceBundle(
        fetched_at="2026-05-27T12:00:00Z",
        project_display_name="Test",
        funnel_overall={"sessions": 1000, "checkouts": 100, "conversion_rate": 0.10}
    )
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=bundle)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    assert brief.affected_region != "Quebec"
    assert "All Regions (Sandbox)" in brief.affected_region
    assert any(t.status.value == "CALLED (LIVE)" for t in brief.tool_trace)
    assert any(t.status.value == "CALLED (MOCK)" for t in brief.tool_trace)
    assert not any("Conversations MCP" in t.note for t in brief.tool_trace)

def test_live_mode_with_no_bundle_falls_back():
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=None)
    with patch("tools.live_evidence_adapter.LiveEvidenceAdapter.load", return_value=None):
        brief = orchestrator.run("What customer experience friction should we investigate today?")
        # Falls back to demo
        assert brief.affected_region == "Quebec"
        # Tool trace mentions fallback
        assert any(t.status.value == "SKIPPED" and "No live bundle provided" in t.note for t in brief.tool_trace)

def test_snapshot_mode_uses_cache():
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.SNAPSHOT, live_bundle=None)
    bundle = LiveEvidenceBundle(
        fetched_at="2026-05-27T12:00:00Z",
        project_display_name="Test",
        funnel_overall={"sessions": 1000, "checkouts": 100, "conversion_rate": 0.10}
    )
    with patch("tools.live_evidence_adapter.LiveEvidenceAdapter.load", return_value=bundle):
        brief = orchestrator.run("What customer experience friction should we investigate today?")
        assert brief.affected_region != "Quebec"
        assert any(t.status.value == "CALLED (SNAPSHOT)" for t in brief.tool_trace)
