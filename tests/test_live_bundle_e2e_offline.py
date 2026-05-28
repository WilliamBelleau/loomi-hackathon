import pytest
from agent.orchestrator import Orchestrator
from agent.schemas import EvidenceMode
from tools.live_evidence_adapter import LiveEvidenceBundle

def test_live_bundle_e2e_offline():
    bundle = LiveEvidenceBundle(
        fetched_at="2026-05-27T12:00:00Z",
        project_display_name="Test Project",
        funnel_overall={"sessions": 1000, "checkouts": 200, "conversion_rate": 0.2},
        funnel_mobile={"sessions": 500, "checkouts": 50, "conversion_rate": 0.1},
        checkout_trend=[{"date": "2026-05-26", "count": 10}],
        cart_trend=[{"date": "2026-05-26", "count": 50}],
        device_breakdown=[{"device": "Mobile", "count": 500}, {"device": "Desktop", "count": 500}],
        campaign_activity=[]
    )
    
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=bundle)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    
    assert brief is not None
    
    # Assert brief uses live analytics evidence
    assert any("LIVE BLOOMREACH MCP" in ev for ev in brief.evidence)
    
    # Assert synthetic ops remains synthetic
    assert any("SYNTHETIC COMMERCE OPS" in ev for ev in brief.evidence)
    
    # Assert no mock region live claim
    assert "All regions / sandbox dataset" not in brief.affected_region
    
    # Assert output remains human-reviewed and simulated-only
    assert brief.human_review_required is True
    assert brief.simulated_actions_only is True
