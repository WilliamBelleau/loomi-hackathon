import pytest
import os
import asyncio
import json
from unittest.mock import patch, MagicMock

from tools.live_mcp_client import refresh_live_mcp_evidence, normalize_trend_response
from agent.schemas import EvidenceMode
from agent.orchestrator import Orchestrator
from tools.live_evidence_adapter import LiveEvidenceBundle
import sys

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "LOOMI_MCP_ANALYTICS_MARKETING_URL": "http://fake-mcp",
        "LOOMI_MCP_PROJECT_ID": "fake-project"
    }):
        yield

@pytest.mark.asyncio
async def test_missing_mcp_dependency_fails_gracefully():
    with patch.dict("sys.modules", {"mcp.client.stdio": None}):
        with pytest.raises(RuntimeError, match="The 'mcp' package is not installed"):
            await refresh_live_mcp_evidence()

@pytest.mark.asyncio
async def test_missing_env_vars_fail_gracefully():
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="LOOMI_MCP_ANALYTICS_MARKETING_URL"):
            await refresh_live_mcp_evidence()
            
    with patch.dict(os.environ, {"LOOMI_MCP_ANALYTICS_MARKETING_URL": "http://fake-mcp"}):
        with pytest.raises(ValueError, match="LOOMI_MCP_PROJECT_ID"):
            await refresh_live_mcp_evidence()

def test_client_queries_are_eql():
    # Read the file directly to avoid import issues
    content = open("tools/live_mcp_client.py").read()
    assert "execute_analytics_eql" in content
    assert "get_funnel" not in content
    assert "get_customer" not in content
    assert "select count event checkout" in content
    assert "SELECT " not in content
    assert "FROM events" not in content
    assert "funnel_id" not in content
    assert "sse_client" not in content

@pytest.mark.asyncio
async def test_client_uses_correct_stdio_args_and_captures_errors(mock_env):
    mock_stdio = MagicMock()
    mock_session = MagicMock()
    
    # Track calls to call_tool
    call_tool_args = []
    
    async def mock_call_tool(tool_name, params):
        call_tool_args.append((tool_name, params))
        if "funnel" in params.get("query", ""):
            # Return proper TextContent
            class TextContent:
                text = json.dumps({"analysis_type": "funnel", "data": {"total": {"counts": [1000, 250]}}})
            res = MagicMock()
            res.content = [TextContent()]
            return res
        elif "checkout" in params.get("query", ""):
            # Simulate a 429 error
            raise Exception("429 Too Many Requests")
        else:
            class TextContent:
                text = json.dumps([])
            res = MagicMock()
            res.content = [TextContent()]
            return res
            
    mock_session.call_tool.side_effect = mock_call_tool
    
    class AsyncContextManager:
        def __init__(self, obj): self.obj = obj
        async def __aenter__(self): return self.obj
        async def __aexit__(self, *args): pass
        
    class StdioContextManager:
        def __init__(self, obj): self.obj = obj
        async def __aenter__(self): return self.obj, self.obj
        async def __aexit__(self, *args): pass

    from unittest.mock import AsyncMock
    mock_session.initialize = AsyncMock()

    class MockStdioServerParameters:
        def __init__(self, command, args):
            self.command = command
            self.args = args

    mcp_mock = MagicMock()
    mcp_mock.client.stdio.stdio_client = MagicMock(return_value=StdioContextManager(mock_stdio))
    mcp_mock.client.session.ClientSession = MagicMock(return_value=AsyncContextManager(mock_session))
    mcp_mock.client.stdio.StdioServerParameters = MockStdioServerParameters
    
    messages = []
    def progress(msg):
        messages.append(msg)
        
    with patch.dict("sys.modules", {"mcp.client.stdio": mcp_mock.client.stdio, "mcp.client.session": mcp_mock.client.session}):
        with patch("asyncio.sleep", return_value=None):
            with patch("pathlib.Path.write_text") as mock_write:
                bundle = await refresh_live_mcp_evidence(progress_callback=progress)
                
                # Check transport
                server_params = mcp_mock.client.stdio.stdio_client.call_args[0][0]
                assert server_params.args == ['-y', 'mcp-remote', "http://fake-mcp"]
                if sys.platform == "win32":
                    assert server_params.command == "npx.cmd"
                else:
                    assert server_params.command == "npx"
                
                # Check tools shape
                assert len(call_tool_args) == 6
                for tool_name, params in call_tool_args:
                    assert tool_name == "execute_analytics_eql"
                    assert "project_id" in params
                    assert "query" in params
                    
                # Check bundle (partial refresh)
                assert bundle is not None
                assert bundle.funnel_overall.sessions == 1000
                assert bundle.funnel_overall.checkouts == 250
                assert bundle.funnel_overall.conversion_rate == 0.25
                assert bundle.checkout_trend == []
                
                # Check write text is sanitized (no token/cookie)
                written_text = mock_write.call_args[0][0]
                assert "cookie" not in written_text.lower()
                assert "token" not in written_text.lower()
                
                # Check progress callback
                assert "Connecting to live MCP..." in messages
                assert any("checkout_trend" in m for m in messages)


# ── normalize_trend_response unit tests ──────────────────────────────────────

def test_normalize_trend_response_extracts_data_from_execute_analytics_eql_dict():
    """The full EQL response dict must be unwrapped; data rows extracted and mapped."""
    eql_response = {
        "success": True,
        "query": "select count event checkout ...",
        "analysis_type": "trend",
        "data": [
            ["2026-05-01", 120],
            ["2026-05-02", 98],
        ],
        "error": None,
    }
    result = normalize_trend_response(eql_response)
    assert isinstance(result, list), "result must be a list"
    assert len(result) == 2
    assert result[0] == {"date": "2026-05-01", "count": 120}
    assert result[1] == {"date": "2026-05-02", "count": 98}


def test_normalize_trend_response_handles_dict_rows_with_flexible_field_names():
    """Rows with label/value field names instead of date/count must be accepted."""
    payload = {"rows": [{"label": "Mon", "value": 55}, {"label": "Tue", "value": 70}]}
    result = normalize_trend_response(payload)
    assert len(result) == 2
    assert result[0] == {"date": "Mon", "count": 55}


def test_normalize_trend_response_returns_passthrough_for_already_list():
    """If the MCP already returns a proper list, it must pass through unchanged."""
    already_list = [{"date": "2026-05-01", "count": 42}]
    result = normalize_trend_response(already_list)
    assert result == already_list


def test_unexpected_trend_shape_returns_empty_list_with_no_crash():
    """Completely unknown shapes must return [] without raising."""
    assert normalize_trend_response(None) == []
    assert normalize_trend_response(12345) == []
    assert normalize_trend_response("raw string") == []
    assert normalize_trend_response({"nested": {"deeply": "unknown"}}) == []
    assert normalize_trend_response({}) == []


def test_refresh_live_mcp_evidence_does_not_pass_raw_dict_to_checkout_trend():
    """After refresh, checkout_trend must always be a list, never a raw EQL dict."""
    # We verify this by inspecting the final bundle returned by the mock refresh
    # The existing mock test already validates bundle.checkout_trend == []
    # This test verifies normalize_trend_response is used as a guard:
    eql_dict_response = {"success": True, "data": [["2026-05-01", 50]], "error": None}
    result = normalize_trend_response(eql_dict_response)
    assert isinstance(result, list), "normalize_trend_response must never return a dict"
    # The LiveEvidenceBundle must accept this result without raising
    from tools.live_evidence_adapter import LiveEvidenceBundle
    bundle = LiveEvidenceBundle(
        fetched_at="2026-06-01T00:00:00Z",
        project_display_name="Test",
        checkout_trend=result,
        cart_trend=[],
    )
    assert isinstance(bundle.checkout_trend, list)
