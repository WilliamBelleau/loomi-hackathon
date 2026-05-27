import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock

from tools.live_mcp_client import refresh_live_mcp_evidence
from agent.schemas import EvidenceMode
from agent.orchestrator import Orchestrator
from tools.live_evidence_adapter import LiveEvidenceBundle

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {"LOOMI_MCP_ANALYTICS_MARKETING_URL": "http://fake-mcp"}):
        yield

@pytest.mark.asyncio
async def test_missing_mcp_dependency_fails_gracefully():
    # If mcp is missing, it should raise RuntimeError
    with patch.dict("sys.modules", {"mcp.client.sse": None}):
        with pytest.raises(RuntimeError, match="The 'mcp' package is not installed"):
            await refresh_live_mcp_evidence()

@pytest.mark.asyncio
async def test_live_evidence_can_be_normalized(mock_env):
    # Mock the SSE client to return a fake session
    mock_sse = SseMockContextManager()
    mock_session = SessionMockContextManager()
    
    # We will mock the call_tool response with dynamic content based on the intent
    def mock_call_tool(tool_name, params):
        res = MagicMock()
        if "checkout" in params.get("query", "") or "cart" in params.get("query", ""):
            res.content = []
        elif tool_name == "get_funnel":
            res.content = {"sessions": 1000, "checkouts": 250, "conversion_rate": 0.25}
        else:
            res.content = {} if tool_name == "execute_analytics_eql" and "session_start" in params.get("query", "") else []
        return res
    
    from unittest.mock import AsyncMock
    mock_session.obj.call_tool = AsyncMock(side_effect=mock_call_tool)
    mock_session.obj.initialize = AsyncMock(return_value=None)
    
    mock_sse_client = MagicMock()
    mock_sse_client.return_value = mock_sse
    mock_client_session = MagicMock()
    mock_client_session.return_value = mock_session

    mcp_mock = MagicMock()
    mcp_mock.client.sse.sse_client = mock_sse_client
    mcp_mock.client.session.ClientSession = mock_client_session
    
    with patch.dict("sys.modules", {"mcp.client.sse": mcp_mock.client.sse, "mcp.client.session": mcp_mock.client.session}):
        with patch("asyncio.sleep", return_value=None):  # Skip rate limiting sleep in tests
            bundle = await refresh_live_mcp_evidence()
            assert isinstance(bundle, LiveEvidenceBundle)
            assert bundle.funnel_overall.model_dump() == {"sessions": 1000, "checkouts": 250, "conversion_rate": 0.25}

def test_failed_live_refresh_does_not_break_demo_mode():
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.DEMO)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    assert brief.affected_region == "Quebec"

def test_run_triage_uses_live_evidence_when_provided():
    bundle = LiveEvidenceBundle(
        fetched_at="2026-05-27T12:00:00Z",
        project_display_name="Test",
        funnel_overall={"sessions": 1000, "checkouts": 100, "conversion_rate": 0.10}
    )
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=bundle)
    brief = orchestrator.run("What customer experience friction should we investigate today?")
    # Live mode should use the provided bundle
    assert brief.affected_region == "All Regions (Sandbox)"
    # Ensure it's using the LIVE trace
    assert any("LIVE BLOOMREACH MCP" in t.adapter for t in brief.tool_trace)

def test_run_triage_falls_back_cleanly_when_live_unavailable():
    # If mode is LIVE but no bundle provided, it should fall back to SNAPSHOT or DEMO
    orchestrator = Orchestrator(evidence_mode=EvidenceMode.LIVE, live_bundle=None)
    # We mock LiveEvidenceAdapter.load to return None, forcing fallback to DEMO
    with patch("tools.live_evidence_adapter.LiveEvidenceAdapter.load", return_value=None):
        brief = orchestrator.run("What customer experience friction should we investigate today?")
        # Should have fallen back to demo mode data
        assert any(t.status.value == "SKIPPED" and "No live bundle provided" in t.note for t in brief.tool_trace)

class SseMockContextManager:
    def __init__(self):
        self.obj = MagicMock()
    async def __aenter__(self):
        return self.obj, self.obj
    async def __aexit__(self, exc_type, exc, tb):
        pass

class SessionMockContextManager:
    def __init__(self):
        self.obj = MagicMock()
    async def __aenter__(self):
        return self.obj
    async def __aexit__(self, exc_type, exc, tb):
        pass
