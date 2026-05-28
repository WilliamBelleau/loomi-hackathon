import pytest
import os
import sys

# Opt-in live E2E
@pytest.mark.live_mcp
@pytest.mark.skipif(
    not os.environ.get("RUN_LIVE_MCP_E2E"),
    reason="RUN_LIVE_MCP_E2E not set"
)
@pytest.mark.asyncio
async def test_live_mcp_e2e():
    url = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL")
    project_id = os.environ.get("LOOMI_MCP_PROJECT_ID")
    
    assert url, "LOOMI_MCP_ANALYTICS_MARKETING_URL is required"
    assert project_id, "LOOMI_MCP_PROJECT_ID is required"
    
    try:
        from mcp.client.stdio import stdio_client, StdioServerParameters
        from mcp.client.session import ClientSession
    except ImportError:
        pytest.fail("mcp package is required for live E2E")

    server_params = StdioServerParameters(
        command="npx.cmd" if sys.platform == "win32" else "npx",
        args=["-y", "mcp-remote", url]
    )
    
    import json
    
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Use one safe aggregate query
            query = "funnel session_start followed by checkout in last 14 days end"
            result = await session.call_tool(
                "execute_analytics_eql",
                {"project_id": project_id, "query": query}
            )
            
            # Extract content and assert shape
            parsed = json.loads(result.content[0].text)
            
            assert parsed.get("success") is True
            assert parsed.get("analysis_type") == "funnel"
            
            counts = parsed.get("data", {}).get("total", {}).get("counts", [])
            assert len(counts) >= 2
            sessions = counts[0]
            checkouts = counts[1]
            
            assert isinstance(sessions, (int, float))
            assert isinstance(checkouts, (int, float))
            
            conversion_rate = checkouts / sessions if sessions > 0 else 0
            assert 0 <= conversion_rate <= 1
            
            # Source label validation (simulated in LiveEvidenceBundle, but here we just assert shape)
            assert "email" not in str(parsed).lower()
            assert "customer_id" not in str(parsed).lower()
