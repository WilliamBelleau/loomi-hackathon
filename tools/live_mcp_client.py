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
        from mcp.client.sse import sse_client
        from mcp.client.session import ClientSession
    except ImportError:
        raise RuntimeError("The 'mcp' package is not installed. Please install requirements-mcp.txt.")

    mcp_url = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL")
    if not mcp_url:
        raise ValueError("LOOMI_MCP_ANALYTICS_MARKETING_URL environment variable is not set.")

    if progress_callback:
        progress_callback(f"Connecting to {mcp_url} ...")

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

    try:
        async with sse_client(mcp_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                queries = [
                    ("checkout_trend", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='checkout' AND timestamp >= now() - 14d GROUP BY date"}),
                    ("cart_trend", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='cart_update' AND timestamp >= now() - 14d GROUP BY date"}),
                    ("funnel_overall", "get_funnel", {"funnel_id": "session_to_checkout"}),
                    ("funnel_mobile", "get_funnel", {"funnel_id": "mobile_session_to_checkout"}),
                    ("campaign_activity", "execute_analytics_eql", {"query": "SELECT count() FROM campaigns WHERE timestamp >= now() - 14d GROUP BY date, action_type"}),
                    ("device_breakdown", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='session_start' GROUP BY device"})
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
