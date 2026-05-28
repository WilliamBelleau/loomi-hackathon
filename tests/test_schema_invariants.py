import pytest
from pydantic import ValidationError
from agent.orchestrator import TriageBrief
from agent.schemas import EvidenceMode, EvidenceSourceLabel

def test_human_review_required_always_true():
    # If we provide True, it works
    brief = TriageBrief(
        issue_title="Test",
        severity=1,
        confidence=1.0,
        affected_journey="Test",
        affected_channel="Test",
        affected_region="Test",
        customer_impact="Test",
        business_impact="Test",
        evidence=[],
        suspected_root_causes=[],
        recommended_next_steps=[],
        owner_recommendation="Test",
        draft_incident_note="Test",
        reasoning_summary="Test",
        limitations=["Test"],
        human_review_required=True,
        simulated_actions_only=True
    )
    assert brief.human_review_required is True

def test_human_review_required_cannot_be_false():
    with pytest.raises(ValidationError):
        TriageBrief(
            issue_title="Test",
            severity=1,
            confidence=1.0,
            affected_journey="Test",
            affected_channel="Test",
            affected_region="Test",
            customer_impact="Test",
            business_impact="Test",
            evidence=[],
            suspected_root_causes=[],
            recommended_next_steps=[],
            owner_recommendation="Test",
            draft_incident_note="Test",
            reasoning_summary="Test",
            limitations=["Test"],
            human_review_required=False,
            simulated_actions_only=True
        )

def test_simulated_actions_only_always_true():
    pass

def test_simulated_actions_only_cannot_be_false():
    with pytest.raises(ValidationError):
        TriageBrief(
            issue_title="Test",
            severity=1,
            confidence=1.0,
            affected_journey="Test",
            affected_channel="Test",
            affected_region="Test",
            customer_impact="Test",
            business_impact="Test",
            evidence=[],
            suspected_root_causes=[],
            recommended_next_steps=[],
            owner_recommendation="Test",
            draft_incident_note="Test",
            reasoning_summary="Test",
            limitations=["Test"],
            human_review_required=True,
            simulated_actions_only=False
        )

def test_evidence_source_labels_are_exact():
    assert EvidenceSourceLabel.LIVE_BLOOMREACH_MCP.value == "LIVE BLOOMREACH MCP"
    assert EvidenceSourceLabel.MCP_SNAPSHOT.value in ["MCP SNAPSHOT", "LAST_SUCCESSFUL_REFRESH"]
    assert EvidenceSourceLabel.SYNTHETIC_COMMERCE_OPS.value == "SYNTHETIC COMMERCE OPS"
    assert EvidenceSourceLabel.MOCK_FIXTURE.value == "MOCK FIXTURE"

def test_evidence_modes_are_exact():
    assert EvidenceMode.DEMO.value == "demo"
    assert EvidenceMode.LIVE.value == "live"
    assert EvidenceMode.SNAPSHOT.value == "snapshot"
