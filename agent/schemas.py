"""
schemas.py — Pydantic data models for the Simons Unified Commerce Signal Agent.

All fields use descriptive names and optional defaults so the models can be
extended cleanly once real Bloomreach MCP schemas are known.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Signal primitives
# ---------------------------------------------------------------------------

class AnalyticsSignal(BaseModel):
    """A single conversion/behavioural anomaly from the Analytics MCP adapter."""

    metric_name: str = Field(..., description="e.g. 'checkout_start_conversion_rate'")
    current_value: float = Field(..., description="Current period value (e.g. 0.34 for 34 %)")
    baseline_value: float = Field(..., description="7-day rolling baseline value")
    delta_pct: float = Field(..., description="Percentage change vs baseline (negative = drop)")
    channel: str = Field(..., description="e.g. 'Mobile Web', 'Desktop'")
    region: str = Field(..., description="e.g. \'All regions (sandbox dataset)\'")
    is_anomaly: bool = Field(default=True)
    notes: Optional[str] = None
    source_label: Optional[str] = Field(
        default=None,
        description="Evidence source badge: one of EvidenceSourceLabel values. None = MOCK_FIXTURE.",
    )


class ConversationSignal(BaseModel):
    """A rising customer intent or friction theme from the Conversations MCP adapter."""

    intent_name: str = Field(..., description="e.g. 'payment_failed'")
    spike_pct: float = Field(..., description="Percentage increase in intent volume")
    representative_phrases: List[str] = Field(default_factory=list)
    channel: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None


class OpsSignal(BaseModel):
    """A synthetic operations signal (payment, OMS, fulfillment, etc.)."""

    system: str = Field(..., description="e.g. 'Payment Gateway', 'OMS'")
    error_type: str = Field(..., description="e.g. 'authorization_failure'")
    error_rate: float = Field(..., description="Current error rate (0–1 fraction)")
    threshold: float = Field(..., description="Alert threshold (0–1 fraction)")
    threshold_breached: bool = Field(default=True)
    affected_path: Optional[str] = None
    notes: Optional[str] = None


class MarketingContext(BaseModel):
    """Optional marketing/campaign context to rule out demand-driven anomalies."""

    campaign_name: Optional[str] = None
    traffic_spike_detected: bool = Field(
        default=False,
        description=(
            "True only if an active campaign could independently explain the anomaly. "
            "When False, a campaign is NOT a plausible alternative explanation."
        ),
    )
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Evidence bundle
# ---------------------------------------------------------------------------

class EvidenceBundle(BaseModel):
    """Aggregated evidence from all signal adapters for a single triage run."""

    analytics_signals: List[AnalyticsSignal] = Field(default_factory=list)
    conversation_signals: List[ConversationSignal] = Field(default_factory=list)
    ops_signals: List[OpsSignal] = Field(default_factory=list)
    marketing_context: Optional[MarketingContext] = None


# ---------------------------------------------------------------------------
# Tool trace
# ---------------------------------------------------------------------------

class TraceStatus(str, Enum):
    CALLED_MOCK = "CALLED (MOCK)"
    CALLED_LIVE = "CALLED (LIVE)"
    CALLED_SNAPSHOT = "CALLED (SNAPSHOT)"
    SKIPPED = "SKIPPED"


class EvidenceMode(str, Enum):
    """Controls which evidence source the orchestrator uses."""

    DEMO = "demo"          # default — mock fixture data, always fast
    LIVE = "live"          # live call to MCP
    SNAPSHOT = "snapshot"  # Last Successful MCP Refresh


class EvidenceSourceLabel(str, Enum):
    """Source label attached to each evidence item in the triage brief UI."""

    LIVE_BLOOMREACH_MCP = "LIVE BLOOMREACH MCP"
    MCP_SNAPSHOT = "MCP SNAPSHOT"
    SYNTHETIC_COMMERCE_OPS = "SYNTHETIC COMMERCE OPS"
    MOCK_FIXTURE = "MOCK FIXTURE"


class ToolTraceEntry(BaseModel):
    """Records a single adapter call during orchestration."""

    adapter: str
    status: TraceStatus
    signal_count: int = 0
    note: str = ""


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

class ScoringResult(BaseModel):
    """Transparent severity/confidence scores with per-signal reasoning."""

    severity: int = Field(..., ge=1, le=5, description="1 = low, 5 = critical")
    confidence: float = Field(..., ge=0.0, le=1.0, description="0 = no signal, 1 = certain")
    reasoning: List[str] = Field(default_factory=list, description="Plain-text explanation per factor")


# ---------------------------------------------------------------------------
# Triage brief — final structured output
# ---------------------------------------------------------------------------

class TriageBrief(BaseModel):
    """
    The complete triage output produced by the orchestrator.

    Fields map 1-to-1 with the demo UI sections.
    human_review_required and simulated_actions_only are ALWAYS True.
    """

    issue_title: str
    severity: int = Field(..., ge=1, le=5)
    confidence: float = Field(..., ge=0.0, le=1.0)
    affected_journey: str
    affected_channel: str
    affected_region: str
    customer_impact: str
    business_impact: str
    evidence: List[str] = Field(default_factory=list)
    suspected_root_causes: List[str] = Field(default_factory=list)
    recommended_next_steps: List[str] = Field(default_factory=list)
    owner_recommendation: str
    draft_incident_note: str
    human_review_required: Literal[True] = True
    simulated_actions_only: Literal[True] = True
    tool_trace: List[ToolTraceEntry] = Field(default_factory=list)
    reasoning_summary: str = ""
    limitations: List[str] = Field(default_factory=list)
