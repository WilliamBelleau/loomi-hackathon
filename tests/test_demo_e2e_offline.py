import pytest
from agent.orchestrator import Orchestrator
from agent.schemas import EvidenceMode

def test_demo_e2e_offline():
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.DEMO)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    
    assert brief is not None
    assert brief.issue_title
    assert isinstance(brief.severity, int)
    assert 1 <= brief.severity <= 5
    assert isinstance(brief.confidence, float)
    assert 0.0 <= brief.confidence <= 1.0
    
    assert len(brief.evidence) > 0
    assert brief.owner_recommendation
    assert brief.draft_incident_note
    
    assert brief.human_review_required is True
    assert brief.simulated_actions_only is True
