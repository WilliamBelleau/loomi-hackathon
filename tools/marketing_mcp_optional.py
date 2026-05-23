"""
marketing_mcp_optional.py — Optional Marketing MCP Adapter (MOCKED).

Current state: returns a stub MarketingContext with no campaign spike,
reflecting the primary demo scenario (the anomaly is not explained by
marketing activity).

Phase 2 replacement:
  Replace the body of get_context() with a real Bloomreach Marketing MCP
  tool call. Example (placeholder — exact schema TBD by Bloomreach):

    # result = await session.call_tool("loomi_marketing_get_campaign_context", {...})
    # return MarketingContext(**result)

Role in scoring:
  traffic_spike_detected = True  → reduces confidence in payment root-cause hypothesis
  traffic_spike_detected = False → no scoring impact (does NOT reduce confidence
                                   that a customer-impacting issue exists)

No network calls are made in the current implementation.
"""
from __future__ import annotations

from agent.schemas import MarketingContext


class MarketingMCPClientOptional:
    """
    Optional adapter for Bloomreach Loomi Connect Marketing MCP.

    MOCKED: Returns a static context stub.
    Used to rule out demand-driven explanations for checkout anomalies.
    """

    def get_context(self) -> MarketingContext:
        """
        Return marketing/campaign context for the current period.

        Default fixture: no campaign spike — the checkout anomaly is not
        attributable to marketing-driven demand surge.
        """
        return MarketingContext(
            campaign_name=None,
            traffic_spike_detected=False,
            notes=(
                "No active campaign with meaningful traffic spike detected "
                "in the Quebec / Mobile Web segment. "
                "Demand surge is not a plausible alternative explanation."
            ),
        )
