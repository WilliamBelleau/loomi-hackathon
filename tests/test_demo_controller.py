import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agent.schemas import EvidenceMode
from app.demo_controller import (
    run_triage_for_ui,
    write_demo_artifact,
    _sanitize_string
)

@pytest.fixture
def mock_brief():
    from agent.schemas import TriageBrief, TraceStatus, ToolTraceEntry

    return TriageBrief(
        issue_title="Mock Issue",
        severity=4,
        confidence=0.85,
        evidence=["[Analytics] Checkout drop", "Some url: https://loomi-mcp-alpha.bloomreach.com/mcp", "Project: 952be3a0"],
        suspected_root_causes=["A", "B"],
        owner_recommendation="Owner",
        recommended_next_steps=["Step 1"],
        draft_incident_note="Incident with project 952be3a0 at https://loomi-mcp-alpha.bloomreach.com/mcp",
        reasoning_summary="Reasoning",
        tool_trace=[ToolTraceEntry(adapter="MockAdapter", status=TraceStatus.CALLED_MOCK, signal_count=1)],
        limitations=["Limitation 1"],
        customer_impact="High",
        business_impact="Medium",
        affected_journey="Checkout",
        affected_channel="Mobile",
        affected_region="Quebec"
    )

def test_run_triage_offline_demo_mode():
    brief = run_triage_for_ui(EvidenceMode.DEMO)
    assert brief is not None
    assert brief.issue_title is not None
    assert brief.severity > 0
    assert brief.human_review_required is True

def test_sanitize_string():
    raw_text = "Connect to https://loomi-mcp-alpha.bloomreach.com/mcp for 952be3a0."
    with patch.dict(os.environ, {"LOOMI_MCP_ANALYTICS_MARKETING_URL": "https://loomi-mcp-alpha.bloomreach.com/mcp", "LOOMI_MCP_PROJECT_ID": "952be3a0"}):
        sanitized = _sanitize_string(raw_text)
        assert "loomi-mcp-alpha" not in sanitized
        assert "952be3a0" not in sanitized
        assert "<REDACTED_ENDPOINT>" in sanitized
        assert "<REDACTED_PROJECT_ID>" in sanitized

def test_write_demo_artifact(mock_brief, tmp_path):
    # Override ARTIFACTS_DIR for testing
    from app import demo_controller

    with patch.object(demo_controller, 'ARTIFACT_MD', tmp_path / "demo_autopilot_latest.md"), \
         patch.object(demo_controller, 'ARTIFACT_JSON', tmp_path / "demo_autopilot_latest.json"), \
         patch.object(demo_controller, 'ARTIFACTS_DIR', tmp_path), \
         patch.dict(os.environ, {"LOOMI_MCP_ANALYTICS_MARKETING_URL": "https://loomi-mcp-alpha.bloomreach.com/mcp", "LOOMI_MCP_PROJECT_ID": "952be3a0"}):

        write_demo_artifact(mock_brief, EvidenceMode.DEMO.value, "Test Source")

        md_file = tmp_path / "demo_autopilot_latest.md"
        json_file = tmp_path / "demo_autopilot_latest.json"

        assert md_file.exists()
        assert json_file.exists()

        md_content = md_file.read_text(encoding="utf-8")
        assert "Mock Issue" in md_content
        assert "loomi-mcp-alpha" not in md_content
        assert "952be3a0" not in md_content
        assert "REDACTED" in md_content

        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        assert json_data["_meta"]["mode"] == "demo"
        json_str = json.dumps(json_data)
        assert "loomi-mcp-alpha" not in json_str
        assert "952be3a0" not in json_str
        assert "REDACTED" in json_str
