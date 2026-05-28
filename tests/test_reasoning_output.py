import pytest
from unittest.mock import patch
from agent.orchestrator import Orchestrator
from agent.schemas import EvidenceMode
from tools.live_evidence_adapter import LiveEvidenceBundle

def test_reasoning_output_contract():
    bundle = LiveEvidenceBundle(
        fetched_at="2026-05-27T12:00:00Z",
        project_display_name="Test",
        funnel_overall={"sessions": 1000, "checkouts": 100, "conversion_rate": 0.10}
    )
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=bundle)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    
    # Assert evidence strings include source labels
    assert any("LIVE BLOOMREACH MCP" in ev or "SYNTHETIC COMMERCE OPS" in ev or "MOCK FIXTURE" in ev for ev in brief.evidence)
    
    # Assert no "facade"
    brief_str = str(brief.model_dump()).lower()
    assert "facade" not in brief_str
    
    # Assert no "Conversations MCP" for the synthetic customer voice fixture in the actual output
    output_text = (brief.reasoning_summary + " ".join(brief.evidence) + " ".join(brief.suspected_root_causes)).lower()
    assert "conversations mcp" not in output_text
    
    # Assert limitations note about sandbox geography
    assert any("sandbox" in lim.lower() for lim in brief.limitations)
    
    # Assert draft incident note contains human-review language
    assert "simulated" in brief.draft_incident_note.lower() or "review" in brief.draft_incident_note.lower()
    
    # Assert recommended owner is present
    assert brief.owner_recommendation
