"""
scoring.py — Transparent, additive severity and confidence scoring.

Every point of severity or confidence is traceable to a named signal.
No black-box logic. No ML. Designed so judges and reviewers can follow the math.

Scoring rules:
  Severity (1–5):
    Base:                                          1
    Analytics: conversion drop > 10 %:           +1
    Analytics: conversion drop > 20 %:           +1  (additive)
    Conversations: any intent spike > 30 %:       +1
    Ops: any threshold-breached error:            +1

  Confidence (0.0–1.0):
    Starts at 0.0
    Analytics anomaly detected:                  +0.30
    Conversations spike correlated to channel:   +0.30
    Ops signal correlated to same failure type:  +0.25
    Multiple signals share same region/channel:  +0.15 (overlap bonus)
    Marketing spike explains anomaly:            -0.20 (payment hypothesis weakened only)
    Capped at 1.0.
"""
from __future__ import annotations

from agent.schemas import EvidenceBundle, ScoringResult


def score_evidence(bundle: EvidenceBundle) -> ScoringResult:
    """
    Score an EvidenceBundle and return severity (1-5) and confidence (0.0-1.0)
    with a plain-text reasoning list.
    """
    severity = 1
    confidence = 0.0
    reasoning: list[str] = []

    # --- Analytics signals ---
    max_conversion_drop = 0.0
    analytics_anomaly_found = False

    for sig in bundle.analytics_signals:
        if sig.is_anomaly and sig.delta_pct < 0:
            drop = abs(sig.delta_pct)
            max_conversion_drop = max(max_conversion_drop, drop)
            analytics_anomaly_found = True

    if analytics_anomaly_found:
        confidence += 0.30
        reasoning.append(
            f"Analytics: anomaly detected — largest conversion drop {max_conversion_drop:.1f}% "
            f"vs baseline. (+0.30 confidence)"
        )
        if max_conversion_drop > 10:
            severity += 1
            reasoning.append(
                f"Analytics: conversion drop > 10% ({max_conversion_drop:.1f}%). (+1 severity)"
            )
        if max_conversion_drop > 20:
            severity += 1
            reasoning.append(
                f"Analytics: conversion drop > 20% ({max_conversion_drop:.1f}%). (+1 severity, additive)"
            )

    # --- Conversation signals ---
    max_intent_spike = 0.0
    conversation_found = False

    for sig in bundle.conversation_signals:
        if sig.spike_pct > 0:
            max_intent_spike = max(max_intent_spike, sig.spike_pct)
            conversation_found = True

    if conversation_found:
        confidence += 0.30
        reasoning.append(
            f"Conversations: rising friction intents detected — largest spike {max_intent_spike:.1f}%. "
            f"(+0.30 confidence)"
        )
        if max_intent_spike > 30:
            severity += 1
            reasoning.append(
                f"Conversations: intent spike > 30% ({max_intent_spike:.1f}%). (+1 severity)"
            )

    # --- Ops signals ---
    ops_breach_found = False
    for sig in bundle.ops_signals:
        if sig.threshold_breached:
            ops_breach_found = True
            break

    if ops_breach_found:
        confidence += 0.25
        severity += 1
        reasoning.append(
            "Ops: at least one threshold-breached error signal detected. (+1 severity, +0.25 confidence)"
        )

    # --- Multi-source correlation bonus ---
    active_source_count = sum([
        analytics_anomaly_found,
        conversation_found,
        ops_breach_found,
    ])
    if active_source_count >= 2:
        confidence += 0.15
        reasoning.append(
            f"Correlation: {active_source_count} independent signal sources corroborate the same "
            f"issue. (+0.15 confidence)"
        )

    # --- Marketing context — narrows payment hypothesis only ---
    if bundle.marketing_context and bundle.marketing_context.traffic_spike_detected:
        confidence -= 0.20
        reasoning.append(
            "Marketing: an active campaign traffic spike was detected. "
            "This weakens confidence in a payment/ops root-cause hypothesis "
            "(demand surge may explain checkout pressure). (-0.20 confidence)"
        )

    # Clamp values
    severity = max(1, min(5, severity))
    confidence = round(max(0.0, min(1.0, confidence)), 2)

    return ScoringResult(severity=severity, confidence=confidence, reasoning=reasoning)
