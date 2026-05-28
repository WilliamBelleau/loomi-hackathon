"""
live_mcp_client.py — Real live MCP client for Streamlit workflow.

Executes sequential queries via the Python MCP SDK to retrieve real analytics
data, rate limiting calls to avoid server rejection.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from tools.live_evidence_adapter import LiveEvidenceBundle

CACHE_FILE_PATH = Path(__file__).parent.parent / "data" / "live_evidence_cache.json"

async def refresh_live_mcp_evidence(progress_callback: Optional[Callable[[str], None]] = None) -> LiveEvidenceBundle:
    """
    Connects to the Bloomreach Analytics MCP and executes the designated EQL queries.
    Saves the output to data/live_evidence_cache.json and returns a LiveEvidenceBundle.
    """
    try:
        from mcp.client.stdio import stdio_client, StdioServerParameters
        from mcp.client.session import ClientSession
    except ImportError:
        raise RuntimeError("The 'mcp' package is not installed. Please install requirements-mcp.txt.")

    mcp_url = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL")
    if not mcp_url:
        raise ValueError("LOOMI_MCP_ANALYTICS_MARKETING_URL environment variable is not set.")
    if mcp_url.endswith("/"):
        raise ValueError("LOOMI_MCP_ANALYTICS_MARKETING_URL must not have a trailing slash.")

    project_id = os.environ.get("LOOMI_MCP_PROJECT_ID")
    if not project_id:
        raise ValueError("LOOMI_MCP_PROJECT_ID environment variable is not set.")

    if progress_callback:
        progress_callback("Connecting to live MCP...")

    snapshot_data = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "project_display_name": "Unknown Sandbox",
        "capture_method": "tools/live_mcp_client.py",
        "source": "LOOMI_MCP_ANALYTICS_MARKETING_URL",
        "checkout_trend": [],
        "cart_trend": [],
        "funnel_overall": {},
        "funnel_mobile": {},
        "campaign_activity": [],
        "device_breakdown": {},
        "queries_attempted": 0,
        "queries_succeeded": 0,
        "errors": []
    }

    server_params = StdioServerParameters(
        command="npx.cmd" if sys.platform == "win32" else "npx",
        args=["-y", "mcp-remote", mcp_url]
    )

    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                queries = [
                    ("checkout_trend", "execute_analytics_eql", {"project_id": project_id, "query": "select count event checkout by row any event timestamp grouping top 14 format year month day in last 14 days"}),
                    ("cart_trend", "execute_analytics_eql", {"project_id": project_id, "query": "select count event cart_update by row any event timestamp grouping top 14 format year month day in last 14 days"}),
                    ("device_breakdown", "execute_analytics_eql", {"project_id": project_id, "query": "select count event session_start by event session_start.device grouping top 10 in last 7 days"}),
                    ("campaign_activity", "execute_analytics_eql", {"project_id": project_id, "query": "select count event campaign by row any event timestamp grouping top 14 format year month day by column event campaign.action_type grouping top 5 in last 14 days"}),
                    ("funnel_overall", "execute_analytics_eql", {"project_id": project_id, "query": "funnel session_start followed by checkout in last 14 days end"}),
                    ("funnel_mobile", "execute_analytics_eql", {"project_id": project_id, "query": "funnel session_start where .device is in [\"Android\", \"iPhone\", \"iPad\"] followed by checkout in last 14 days end"})
                ]

                for idx, (intent, tool_name, params) in enumerate(queries):
                    snapshot_data["queries_attempted"] += 1
                    if progress_callback:
                        progress_callback(f"Executing query: {intent} via {tool_name}...")
                    
                    try:
                        result = await session.call_tool(tool_name, params)
                        snapshot_data[intent] = result.content
                        snapshot_data["queries_succeeded"] += 1
                        if progress_callback:
                            progress_callback(f"Success: {intent}")
                    except Exception as e:
                        if progress_callback:
                            progress_callback(f"Failed: {intent} - {str(e)}")
                        snapshot_data["errors"].append(f"{intent} failed: {str(e)}")

                    if idx < len(queries) - 1:
                        if progress_callback:
                            progress_callback("Rate limiting: sleeping for 15 seconds...")
                        await asyncio.sleep(15)

    except Exception as e:
        raise RuntimeError(f"Failed to connect or initialize session: {e}")

    # Write to cache
    CACHE_FILE_PATH.parent.mkdir(exist_ok=True)
    CACHE_FILE_PATH.write_text(json.dumps(snapshot_data, indent=2))

    return LiveEvidenceBundle(**snapshot_data)
