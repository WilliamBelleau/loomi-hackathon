"""
analytics_mcp.py — Analytics MCP Adapter (MOCKED).

Current state: loads synthetic fixture data from data/analytics_anomalies.json.

Phase 2 replacement:
  Replace the body of get_anomalies() with a real Bloomreach MCP tool call.
  The method signature and return type do not change.
  Example (placeholder — exact tool name/schema TBD by Bloomreach):

    # from mcp import ClientSession  # or Bloomreach SDK equivalent
    # result = await session.call_tool("loomi_analytics_get_anomalies", {...})
    # return [AnalyticsSignal(**item) for item in result["signals"]]

No network calls are made in the current implementation.
"""
from __future__ import annotations

import json
from pathlib import Path

from agent.schemas import AnalyticsSignal

_FIXTURE_PATH = Path(__file__).parent.parent / "data" / "analytics_anomalies.json"


class AnalyticsMCPClient:
    """
    Adapter for the Bloomreach Loomi Connect Analytics MCP.

    MOCKED: Returns synthetic fixture data.
    Replace get_anomalies() body with real MCP call once Bloomreach provides
    sandbox credentials, endpoint, and tool schema.
    """

    def get_anomalies(self) -> list[AnalyticsSignal]:
        """Return a list of detected analytics anomalies."""
        raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        return [AnalyticsSignal(**item) for item in raw]
