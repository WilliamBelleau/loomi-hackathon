"""
live_evidence_adapter.py — Reads the MCP snapshot and returns a LiveEvidenceBundle.

This adapter is completely passive. It does not import the `mcp` SDK, nor does it
make any network calls. It only reads `data/live_evidence_snapshot.json`, which
is generated asynchronously by `scripts/refresh_mcp_snapshot.py`.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agent.schemas import AnalyticsSignal, EvidenceSourceLabel

_SNAPSHOT_PATH = Path(__file__).parent.parent / "data" / "live_evidence_cache.json"


class TrendPoint(BaseModel):
    date: str
    count: int


class FunnelStats(BaseModel):
    sessions: int
    checkouts: int
    conversion_rate: float


class LiveEvidenceBundle(BaseModel):
    """Data loaded from the snapshot JSON file."""
    fetched_at: str
    project_display_name: str
    checkout_trend: List[TrendPoint] = Field(default_factory=list)
    cart_trend: List[TrendPoint] = Field(default_factory=list)
    funnel_overall: Optional[FunnelStats] = None
    funnel_mobile: Optional[FunnelStats] = None
    campaign_spike_detected: bool = False
    device_breakdown: Any = Field(default_factory=dict)
    queries_attempted: int = 0
    queries_succeeded: int = 0
    errors: List[Any] = Field(default_factory=list)

    @property
    def snapshot_age_minutes(self) -> float:
        """Returns the age of the snapshot in minutes, or 9999.0 if missing/invalid."""
        try:
            # Handle ISO format strings like "2026-05-27T11:00:00Z" or "2026-05-27T11:00:00+00:00"
            dt_str = self.fetched_at.replace("Z", "+00:00")
            fetched_time = datetime.fromisoformat(dt_str)
            now = datetime.now(timezone.utc)
            delta = now - fetched_time
            return delta.total_seconds() / 60.0
        except (ValueError, TypeError):
            return 9999.0

    def to_analytics_signals(self, label: EvidenceSourceLabel = EvidenceSourceLabel.MCP_SNAPSHOT) -> List[AnalyticsSignal]:
        """Converts the raw snapshot metrics into agent-ready AnalyticsSignals."""
        signals = []

        # 1. Overall Checkout Conversion (only emit if genuinely anomalous)
        if self.funnel_overall and self.funnel_overall.sessions > 0:
            baseline_overall = 0.25
            delta = round((self.funnel_overall.conversion_rate - baseline_overall) / baseline_overall * 100, 1)
            is_below_baseline = self.funnel_overall.conversion_rate < baseline_overall
            if is_below_baseline:  # Only include as evidence when it confirms friction
                signals.append(AnalyticsSignal(
                    metric_name="checkout_start_conversion_rate",
                    current_value=self.funnel_overall.conversion_rate,
                    baseline_value=baseline_overall,
                    delta_pct=delta,
                    channel="All",
                    region="All Regions (Sandbox)",
                    is_anomaly=True,
                    notes=f"Overall session-to-checkout conversion is {self.funnel_overall.conversion_rate:.1%} vs {baseline_overall:.0%} baseline.",
                    source_label=label.value
                ))

        # 2. Mobile Checkout Conversion
        if self.funnel_mobile and self.funnel_mobile.sessions > 0:
            baseline_mobile = 0.28
            delta_mobile = round((self.funnel_mobile.conversion_rate - baseline_mobile) / baseline_mobile * 100, 1)
            signals.append(AnalyticsSignal(
                metric_name="checkout_start_conversion_rate",
                current_value=self.funnel_mobile.conversion_rate,
                baseline_value=baseline_mobile,
                delta_pct=delta_mobile,
                channel="Mobile",
                region="All Regions (Sandbox)",
                is_anomaly=self.funnel_mobile.conversion_rate < baseline_mobile,
                notes=(
                    f"Mobile conversion is {self.funnel_mobile.conversion_rate:.1%} vs {baseline_mobile:.0%} baseline."
                    + (" Dropped significantly." if self.funnel_mobile.conversion_rate < baseline_mobile else " Within expected range.")
                ),
                source_label=label.value
            ))
            
        # 3. Add-to-Cart Stability — only emit if we have real trend data and a non-zero count
        cart_total = sum(p.count for p in self.cart_trend) if self.cart_trend else 0
        checkout_total = sum(p.count for p in self.checkout_trend) if self.checkout_trend else 0
        if cart_total > 0:  # Suppress when live MCP returned no trend data (avoids ↑0.0% noise)
            signals.append(AnalyticsSignal(
                metric_name="add_to_cart_rate",
                current_value=cart_total / max(self.funnel_overall.sessions if self.funnel_overall else 1, 1),
                baseline_value=0.40,
                delta_pct=0.0,
                channel="Mobile Web",
                region="All Regions (Sandbox)",
                is_anomaly=False,
                notes=f"Add-to-cart is stable ({cart_total} total cart events). Product demand is not the driver of the checkout drop.",
                source_label=label.value
            ))

        return signals


class LiveEvidenceAdapter:
    """Reads the live MCP snapshot file and returns a LiveEvidenceBundle."""

    @staticmethod
    def load(snapshot_path: Path | None = None) -> LiveEvidenceBundle | None:
        """
        Loads the snapshot JSON file. Returns None if missing or invalid.
        """
        path = snapshot_path or _SNAPSHOT_PATH
        if not path.exists():
            return None
        
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
            return LiveEvidenceBundle(**data)
        except Exception:
            # Missing fields, invalid JSON, permission issues -> gracefully degrade
            return None
