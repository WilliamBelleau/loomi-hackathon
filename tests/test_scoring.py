"""
test_scoring.py — Unit tests for transparent scoring logic.
"""
import pytest

from agent.schemas import (
    AnalyticsSignal,
    ConversationSignal,
    EvidenceBundle,
    MarketingContext,
    OpsSignal,
)
from agent.scoring import score_evidence


def make_analytics(delta_pct: float, is_anomaly: bool = True) -> AnalyticsSignal:
    return AnalyticsSignal(
        metric_name="checkout_start_conversion_rate",
        current_value=0.40 + delta_pct / 100,
        baseline_value=0.40,
        delta_pct=delta_pct,
        channel="Mobile Web",
        region="Quebec",
        is_anomaly=is_anomaly,
    )


def make_conversation(spike_pct: float) -> ConversationSignal:
    return ConversationSignal(intent_name="payment_failed", spike_pct=spike_pct)


def make_ops(error_rate: float, threshold: float, breached: bool) -> OpsSignal:
    return OpsSignal(
        system="Payment Gateway",
        error_type="authorization_failure",
        error_rate=error_rate,
        threshold=threshold,
        threshold_breached=breached,
    )


# ---------------------------------------------------------------------------
# Severity tests
# ---------------------------------------------------------------------------

class TestSeverity:
    def test_base_severity_is_one_with_no_signals(self):
        bundle = EvidenceBundle()
        result = score_evidence(bundle)
        assert result.severity == 1

    def test_severity_increases_with_10pct_drop(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-15.0)])
        result = score_evidence(bundle)
        assert result.severity >= 2

    def test_severity_increases_further_with_20pct_drop(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-25.0)])
        result = score_evidence(bundle)
        assert result.severity >= 3

    def test_severity_increases_with_intent_spike_above_30pct(self):
        bundle = EvidenceBundle(conversation_signals=[make_conversation(35.0)])
        result = score_evidence(bundle)
        assert result.severity >= 2

    def test_severity_increases_with_breached_ops_threshold(self):
        bundle = EvidenceBundle(ops_signals=[make_ops(0.23, 0.05, True)])
        result = score_evidence(bundle)
        assert result.severity >= 2

    def test_severity_capped_at_5(self):
        bundle = EvidenceBundle(
            analytics_signals=[make_analytics(-30.0)],
            conversation_signals=[make_conversation(50.0)],
            ops_signals=[make_ops(0.30, 0.05, True)],
        )
        result = score_evidence(bundle)
        assert result.severity <= 5

    def test_severity_is_at_least_1(self):
        bundle = EvidenceBundle()
        result = score_evidence(bundle)
        assert result.severity >= 1

    def test_non_anomaly_analytics_signal_does_not_increase_severity(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-15.0, is_anomaly=False)])
        result = score_evidence(bundle)
        assert result.severity == 1


# ---------------------------------------------------------------------------
# Confidence tests
# ---------------------------------------------------------------------------

class TestConfidence:
    def test_confidence_starts_at_zero_with_no_signals(self):
        bundle = EvidenceBundle()
        result = score_evidence(bundle)
        assert result.confidence == 0.0

    def test_analytics_anomaly_adds_confidence(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-18.0)])
        result = score_evidence(bundle)
        assert result.confidence >= 0.30

    def test_conversation_signal_adds_confidence(self):
        bundle = EvidenceBundle(conversation_signals=[make_conversation(42.0)])
        result = score_evidence(bundle)
        assert result.confidence >= 0.30

    def test_ops_signal_adds_confidence(self):
        bundle = EvidenceBundle(ops_signals=[make_ops(0.23, 0.05, True)])
        result = score_evidence(bundle)
        assert result.confidence >= 0.25

    def test_multiple_sources_add_correlation_bonus(self):
        bundle = EvidenceBundle(
            analytics_signals=[make_analytics(-18.0)],
            conversation_signals=[make_conversation(42.0)],
        )
        single_bundle = EvidenceBundle(analytics_signals=[make_analytics(-18.0)])
        multi_result = score_evidence(bundle)
        single_result = score_evidence(single_bundle)
        assert multi_result.confidence > single_result.confidence

    def test_confidence_capped_at_1(self):
        bundle = EvidenceBundle(
            analytics_signals=[make_analytics(-30.0)],
            conversation_signals=[make_conversation(50.0)],
            ops_signals=[make_ops(0.30, 0.05, True)],
        )
        result = score_evidence(bundle)
        assert result.confidence <= 1.0

    def test_marketing_spike_reduces_confidence_in_payment_hypothesis(self):
        no_spike = EvidenceBundle(
            analytics_signals=[make_analytics(-18.0)],
            ops_signals=[make_ops(0.23, 0.05, True)],
            marketing_context=MarketingContext(traffic_spike_detected=False),
        )
        with_spike = EvidenceBundle(
            analytics_signals=[make_analytics(-18.0)],
            ops_signals=[make_ops(0.23, 0.05, True)],
            marketing_context=MarketingContext(traffic_spike_detected=True),
        )
        assert score_evidence(with_spike).confidence < score_evidence(no_spike).confidence

    def test_marketing_no_spike_does_not_penalize_confidence(self):
        without_marketing = EvidenceBundle(
            analytics_signals=[make_analytics(-18.0)],
        )
        with_marketing_no_spike = EvidenceBundle(
            analytics_signals=[make_analytics(-18.0)],
            marketing_context=MarketingContext(traffic_spike_detected=False),
        )
        r1 = score_evidence(without_marketing)
        r2 = score_evidence(with_marketing_no_spike)
        assert r2.confidence == r1.confidence

    def test_confidence_is_float(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-18.0)])
        result = score_evidence(bundle)
        assert isinstance(result.confidence, float)


# ---------------------------------------------------------------------------
# Reasoning tests
# ---------------------------------------------------------------------------

class TestReasoning:
    def test_reasoning_list_is_populated_when_signals_present(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-18.0)])
        result = score_evidence(bundle)
        assert len(result.reasoning) > 0

    def test_reasoning_mentions_conversion_drop(self):
        bundle = EvidenceBundle(analytics_signals=[make_analytics(-18.0)])
        result = score_evidence(bundle)
        combined = " ".join(result.reasoning).lower()
        assert "conversion" in combined or "analytics" in combined

    def test_empty_bundle_has_empty_reasoning(self):
        bundle = EvidenceBundle()
        result = score_evidence(bundle)
        assert result.reasoning == []
