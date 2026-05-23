"""
test_orchestrator.py — Integration tests for the Orchestrator pipeline.
"""
import pytest

from agent.orchestrator import Orchestrator
from agent.schemas import TriageBrief, TraceStatus

DEFAULT_PROMPT = "What customer experience friction should we investigate today?"


@pytest.fixture
def orchestrator():
    return Orchestrator()


@pytest.fixture
def brief(orchestrator):
    return orchestrator.run(DEFAULT_PROMPT)


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_run_returns_triage_brief(self, brief):
        assert isinstance(brief, TriageBrief)

    def test_brief_has_issue_title(self, brief):
        assert brief.issue_title and len(brief.issue_title) > 0

    def test_brief_has_severity(self, brief):
        assert 1 <= brief.severity <= 5

    def test_brief_has_confidence(self, brief):
        assert 0.0 <= brief.confidence <= 1.0

    def test_brief_has_evidence(self, brief):
        assert len(brief.evidence) > 0

    def test_brief_has_suspected_root_causes(self, brief):
        assert len(brief.suspected_root_causes) > 0

    def test_brief_has_recommended_next_steps(self, brief):
        assert len(brief.recommended_next_steps) > 0

    def test_brief_has_draft_incident_note(self, brief):
        assert brief.draft_incident_note and len(brief.draft_incident_note) > 0

    def test_brief_has_reasoning_summary(self, brief):
        assert brief.reasoning_summary and len(brief.reasoning_summary) > 0

    def test_brief_has_limitations(self, brief):
        assert len(brief.limitations) > 0


# ---------------------------------------------------------------------------
# Safety invariants — MUST always be True
# ---------------------------------------------------------------------------

class TestSafetyInvariants:
    def test_human_review_required_is_always_true(self, brief):
        assert brief.human_review_required is True

    def test_simulated_actions_only_is_always_true(self, brief):
        assert brief.simulated_actions_only is True

    def test_human_review_required_cannot_be_false(self, orchestrator):
        """Even with a fresh run the invariant holds."""
        result = orchestrator.run(DEFAULT_PROMPT)
        assert result.human_review_required is True

    def test_simulated_actions_only_cannot_be_false(self, orchestrator):
        result = orchestrator.run(DEFAULT_PROMPT)
        assert result.simulated_actions_only is True


# ---------------------------------------------------------------------------
# Tool trace
# ---------------------------------------------------------------------------

class TestToolTrace:
    def test_tool_trace_is_present(self, brief):
        assert len(brief.tool_trace) > 0

    def test_tool_trace_contains_analytics_adapter(self, brief):
        names = [t.adapter for t in brief.tool_trace]
        assert any("Analytics" in n for n in names)

    def test_tool_trace_contains_conversations_adapter(self, brief):
        names = [t.adapter for t in brief.tool_trace]
        assert any("Conversations" in n for n in names)

    def test_tool_trace_contains_synthetic_ops_adapter(self, brief):
        names = [t.adapter for t in brief.tool_trace]
        assert any("Ops" in n for n in names)

    def test_tool_trace_adapters_are_mocked(self, brief):
        """All real adapters should be called with MOCK status."""
        real_adapters = [
            t for t in brief.tool_trace
            if "Analytics" in t.adapter or "Conversations" in t.adapter or "Ops" in t.adapter
        ]
        for adapter in real_adapters:
            assert adapter.status == TraceStatus.CALLED_MOCK

    def test_tool_trace_has_signal_counts(self, brief):
        for entry in brief.tool_trace:
            assert entry.signal_count >= 0


# ---------------------------------------------------------------------------
# Primary demo scenario assertions
# ---------------------------------------------------------------------------

class TestDemoScenario:
    def test_owner_recommendation_is_commerce_payments(self, brief):
        assert "Commerce" in brief.owner_recommendation and "Payments" in brief.owner_recommendation

    def test_affected_channel_is_mobile(self, brief):
        assert "Mobile" in brief.affected_channel

    def test_affected_region_is_quebec(self, brief):
        assert "Quebec" in brief.affected_region

    def test_severity_is_high_for_demo_scenario(self, brief):
        """With all three signals active, severity should be at least 4."""
        assert brief.severity >= 4

    def test_confidence_is_high_for_demo_scenario(self, brief):
        """With all three signals active, confidence should be at least 0.85."""
        assert brief.confidence >= 0.85

    def test_draft_incident_note_includes_simulation_warning(self, brief):
        assert "SIMULATED" in brief.draft_incident_note or "simulated" in brief.draft_incident_note.lower()


# ---------------------------------------------------------------------------
# Prompt classification
# ---------------------------------------------------------------------------

class TestPromptClassification:
    def test_invalid_prompt_raises_value_error(self, orchestrator):
        with pytest.raises(ValueError):
            orchestrator.run("What is the weather today?")

    def test_triage_prompt_succeeds(self, orchestrator):
        result = orchestrator.run("What customer experience friction should we investigate today?")
        assert isinstance(result, TriageBrief)

    def test_alternate_triage_prompt_succeeds(self, orchestrator):
        result = orchestrator.run("Show me the latest commerce anomalies and checkout issues.")
        assert isinstance(result, TriageBrief)
