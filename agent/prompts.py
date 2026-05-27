"""
prompts.py — Reasoning engine abstraction and triage brief assembly.

Design:
  ReasoningEngine is a Protocol (structural subtyping) so any implementation
  can be dropped in without changing the orchestrator.

  DeterministicReasoningEngine is the default: pure Python template logic,
  no network calls, no LLM dependency — reliable for hackathon demos.

TODO / Roadmap (Phase 2):
  Replace DeterministicReasoningEngine with GeminiReasoningEngine or
  VertexAIReasoningEngine. The engine receives the same EvidenceBundle +
  ScoringResult and returns a TriageBrief. The orchestrator does not change.

  Suggested integration point:
    from google import generativeai as genai   # add to requirements.txt
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(build_gemini_prompt(bundle, score))
    # parse structured JSON from response.text into TriageBrief

  No Gemini / Vertex dependency is added here intentionally.
  The abstraction keeps the demo stable without API credentials.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from agent.schemas import EvidenceBundle, ScoringResult, TriageBrief, ToolTraceEntry


# ---------------------------------------------------------------------------
# Prompt helpers
# ---------------------------------------------------------------------------

TRIAGE_KEYWORDS = [
    "friction",
    "investigate",
    "triage",
    "customer experience",
    "commerce",
    "checkout",
    "anomaly",
    "signal",
]


def classify_prompt(user_prompt: str) -> bool:
    """
    Return True if the prompt looks like a unified commerce triage query.
    Simple keyword matching — sufficient for the demo scenario.
    """
    lowered = user_prompt.lower()
    return any(kw in lowered for kw in TRIAGE_KEYWORDS)


def _format_evidence_list(bundle: EvidenceBundle) -> list[str]:
    """Flatten all signals into human-readable evidence strings."""
    items: list[str] = []

    for sig in bundle.analytics_signals:
        direction = "↓" if sig.delta_pct < 0 else "↑"
        label = getattr(sig, "source_label", None) or "MOCK FIXTURE"
        items.append(
            f"[Analytics] [{label}] {sig.metric_name}: {direction}{abs(sig.delta_pct):.1f}% vs baseline "
            f"({sig.channel}, {sig.region})"
        )

    for sig in bundle.conversation_signals:
        phrases = (
            f" — e.g. \"{sig.representative_phrases[0]}\""
            if sig.representative_phrases
            else ""
        )
        label = "MOCK FIXTURE"
        items.append(
            f"[Conversations] [{label}] Intent '{sig.intent_name}' ↑{sig.spike_pct:.1f}%{phrases}"
        )

    for sig in bundle.ops_signals:
        breach = " ⚠ threshold breached" if sig.threshold_breached else ""
        label = "SYNTHETIC COMMERCE OPS"
        items.append(
            f"[Ops] [{label}] {sig.system} — {sig.error_type}: "
            f"{sig.error_rate*100:.1f}% error rate (threshold {sig.threshold*100:.1f}%){breach}"
        )

    if bundle.marketing_context:
        spike = (
            "Campaign traffic spike DETECTED — consider demand-driven explanation."
            if bundle.marketing_context.traffic_spike_detected
            else "No campaign spike detected — demand surge unlikely to explain anomaly."
        )
        label = "MOCK FIXTURE"
        items.append(f"[Marketing] [{label}] {spike}")

    return items


def _build_draft_incident_note(brief_data: dict) -> str:
    """Assemble a Jira-style incident note from triage fields."""
    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(brief_data["recommended_next_steps"]))
    causes = "\n".join(f"  • {c}" for c in brief_data["suspected_root_causes"])
    evidence = "\n".join(f"  • {e}" for e in brief_data["evidence"])

    return f"""\
[DRAFT INCIDENT NOTE — SIMULATED, NOT FILED]
============================================
Title:    {brief_data["issue_title"]}
Severity: {brief_data["severity"]} / 5
Channel:  {brief_data["affected_channel"]}
Region:   {brief_data["affected_region"]}
Journey:  {brief_data["affected_journey"]}
Owner:    {brief_data["owner_recommendation"]}

Customer Impact:
  {brief_data["customer_impact"]}

Business Impact:
  {brief_data["business_impact"]}

Evidence Summary:
{evidence}

Suspected Root Causes:
{causes}

Recommended Next Steps:
{steps}

⚠ HUMAN REVIEW REQUIRED BEFORE ANY ACTION IS TAKEN.
⚠ THIS NOTE IS SIMULATED — NO TICKET HAS BEEN CREATED.
"""


# ---------------------------------------------------------------------------
# ReasoningEngine protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class ReasoningEngine(Protocol):
    """
    Protocol for reasoning engines.

    Any class implementing build_triage_brief() is a valid ReasoningEngine.
    Swap DeterministicReasoningEngine for GeminiReasoningEngine in Phase 2
    without touching the orchestrator.
    """

    def build_triage_brief(
        self,
        bundle: EvidenceBundle,
        score: ScoringResult,
        tool_trace: list[ToolTraceEntry],
    ) -> TriageBrief:
        ...


# ---------------------------------------------------------------------------
# Default engine: deterministic, no network calls
# ---------------------------------------------------------------------------

class DeterministicReasoningEngine:
    """
    Builds a TriageBrief using Python template logic only.
    No LLM, no network calls. Safe for offline hackathon demos.

    Phase 2 replacement: swap this class for GeminiReasoningEngine.
    See module docstring for integration notes.
    """

    def build_triage_brief(
        self,
        bundle: EvidenceBundle,
        score: ScoringResult,
        tool_trace: list[ToolTraceEntry],
    ) -> TriageBrief:

        evidence = _format_evidence_list(bundle)

        # Derive region/channel from strongest analytics signal
        primary_analytics = next(
            (s for s in bundle.analytics_signals if s.is_anomaly and s.delta_pct < 0),
            None,
        )
        channel = primary_analytics.channel if primary_analytics else "Unknown"
        region = primary_analytics.region if primary_analytics else "Unknown"

        # Suspected root causes — derived from signal types present
        root_causes: list[str] = []
        if any(s.threshold_breached for s in bundle.ops_signals):
            root_causes.append(
                "Payment authorization failures on at least one payment path — "
                "possible gateway misconfiguration or processor-side issue."
            )
        if any(s.intent_name == "payment_failed" for s in bundle.conversation_signals):
            root_causes.append(
                "Customer-reported payment failures corroborate the ops-level signal."
            )
        if primary_analytics and abs(primary_analytics.delta_pct) > 10:
            root_causes.append(
                "Checkout funnel drop is isolated to checkout-start, not add-to-cart, "
                "ruling out product demand as the driver."
            )
        if not root_causes:
            root_causes.append("Insufficient signal to isolate root cause — further investigation required.")

        recommended_steps = [
            "Review payment gateway authorization logs for the affected payment path.",
            "Identify whether the error is limited to a specific processor, BIN range, or region.",
            "Prepare a customer service response macro for customers experiencing checkout failures.",
            "Monitor checkout-start conversion rate for recovery over the next 2 hours.",
            "If authorization failure rate does not improve within SLA, escalate to payment processor.",
            "Do NOT take automated customer-facing action without human review.",
        ]

        # Owner from ops + conversations correlation → Commerce + Payments
        owner = "Commerce + Payments Squad"
        for sig in bundle.ops_signals:
            if "payment" in sig.system.lower() or "payment" in sig.error_type.lower():
                owner = "Commerce + Payments Squad"
                break

        # Limitations
        limitations = [
            "All signal data is synthetic — derived from local fixture files, not live Bloomreach MCP.",
            "Analytics MCP adapter is mocked. Real anomaly detection requires Bloomreach sandbox credentials.",
            "Conversations MCP adapter is mocked. Real intent signals require Bloomreach sandbox credentials.",
            "Ops signals are synthetic. Real payment/OMS data requires integration with internal systems.",
            "Reasoning is deterministic template logic. Phase 2 will introduce LLM-based synthesis.",
        ]

        # Severity label mapping
        severity_labels = {1: "LOW", 2: "LOW-MED", 3: "MEDIUM", 4: "HIGH", 5: "CRITICAL"}
        sev_label = severity_labels.get(score.severity, str(score.severity))

        issue_title = (
            f"[{sev_label}] Mobile Checkout Friction — Quebec — "
            f"Payment Authorization Failures Suspected"
        )

        reasoning_summary = (
            f"Severity {score.severity}/5, Confidence {score.confidence:.0%}. "
            + " ".join(score.reasoning)
        )

        brief_data = dict(
            issue_title=issue_title,
            severity=score.severity,
            confidence=score.confidence,
            affected_journey="Checkout — Payment Step",
            affected_channel=channel,
            affected_region=region,
            customer_impact=(
                "Customers on Mobile Web in Quebec are unable to complete checkout. "
                "Payment failures are causing abandoned orders and customer frustration."
            ),
            business_impact=(
                f"Checkout-start conversion is down {abs(primary_analytics.delta_pct) if primary_analytics else '?'}% "
                f"vs the 7-day baseline. Every hour of unresolved checkout failure "
                f"represents material revenue impact and customer trust erosion."
            ),
            evidence=evidence,
            suspected_root_causes=root_causes,
            recommended_next_steps=recommended_steps,
            owner_recommendation=owner,
        )

        draft_note = _build_draft_incident_note(brief_data)

        return TriageBrief(
            **brief_data,
            draft_incident_note=draft_note,
            human_review_required=True,
            simulated_actions_only=True,
            tool_trace=tool_trace,
            reasoning_summary=reasoning_summary,
            limitations=limitations,
        )
