"""
synthetic_ops.py — Synthetic Operations Adapter (MOCK — no real system).

Current state: loads synthetic fixture data from data/commerce_ops_signals.json.

This adapter represents payment gateway, OMS, and fulfillment signals.
In a production integration, this would connect to internal operations
systems or a unified observability platform.

No network calls are made in the current implementation.
"""
from __future__ import annotations

import json
from pathlib import Path

from agent.schemas import OpsSignal

_FIXTURE_PATH = Path(__file__).parent.parent / "data" / "commerce_ops_signals.json"


class SyntheticOpsClient:
    """
    Provides synthetic commerce operations signals (payment, OMS, fulfillment).

    MOCK: Returns fixture data only. No real external system is contacted.
    Replace get_ops_signals() body with real internal system call in Phase 3.
    """

    def get_ops_signals(self) -> list[OpsSignal]:
        """Return a list of synthetic operations error signals."""
        raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        return [OpsSignal(**item) for item in raw]
