"""
orchestrator.py — Agent pipeline for the Simons Unified Commerce Signal Agent.

Pipeline:
  1. Classify user prompt (reject non-triage requests)
  2. Call Analytics MCP adapter (mocked)
  3. Call Conversations MCP adapter (mocked)
  4. Call Synthetic Ops adapter (mocked)
  5. Optionally call Marketing MCP adapter (mocked, skipped if unavailable)
  6. Assemble EvidenceBundle
  7. Score evidence (transparent, additive)
  8. Build TriageBrief via ReasoningEngine
  9. Return TriageBrief (human_review_required and simulated_actions_only always True)
"""
from __future__ import annotations

from agent.prompts import (
    DeterministicReasoningEngine,
    ReasoningEngine,
    classify_prompt,
)
from agent.schemas import EvidenceBundle, ToolTraceEntry, TraceStatus, TriageBrief, EvidenceMode, EvidenceSourceLabel
from agent.scoring import score_evidence
from tools.analytics_mcp import AnalyticsMCPClient
from tools.conversations_mcp import ConversationsMCPClient
from tools.live_evidence_adapter import LiveEvidenceAdapter
from tools.marketing_mcp_optional import MarketingMCPClientOptional
from tools.synthetic_ops import SyntheticOpsClient


class Orchestrator:
    """
    Main agent loop. Accepts a user prompt and returns a TriageBrief.

    Dependency-inject a custom ReasoningEngine for testing or Phase 2 LLM integration.
    All adapter clients default to local fixture-backed mock implementations.
    """

    def __init__(
        self,
        analytics_client: AnalyticsMCPClient | None = None,
        conversations_client: ConversationsMCPClient | None = None,
        ops_client: SyntheticOpsClient | None = None,
        marketing_client: MarketingMCPClientOptional | None = None,
        reasoning_engine: ReasoningEngine | None = None,
        include_marketing: bool = True,
        evidence_mode: EvidenceMode = EvidenceMode.DEMO,
    ) -> None:
        self.analytics_client = analytics_client or AnalyticsMCPClient()
        self.conversations_client = conversations_client or ConversationsMCPClient()
        self.ops_client = ops_client or SyntheticOpsClient()
        self.marketing_client = marketing_client or MarketingMCPClientOptional()
        self.reasoning_engine: ReasoningEngine = reasoning_engine or DeterministicReasoningEngine()
        self.include_marketing = include_marketing
        self.evidence_mode = evidence_mode

    def run(self, user_prompt: str) -> TriageBrief:
        """
        Execute the full triage pipeline.

        Raises:
            ValueError: if the prompt is not recognized as a triage query.
        """
        if not classify_prompt(user_prompt):
            raise ValueError(
                "Prompt not recognized as a unified commerce triage request. "
                "Try: 'What customer experience friction should we investigate today?'"
            )

        tool_trace: list[ToolTraceEntry] = []

        # Step 1 — Analytics MCP adapter
        analytics_signals = None
        if self.evidence_mode in (EvidenceMode.SNAPSHOT, EvidenceMode.LIVE):
            bundle_snapshot = LiveEvidenceAdapter.load()
            if bundle_snapshot:
                label = (EvidenceSourceLabel.LIVE_BLOOMREACH_MCP 
                         if self.evidence_mode == EvidenceMode.LIVE 
                         else EvidenceSourceLabel.MCP_SNAPSHOT)
                analytics_signals = bundle_snapshot.to_analytics_signals(label=label)
                status = (TraceStatus.CALLED_LIVE 
                          if self.evidence_mode == EvidenceMode.LIVE 
                          else TraceStatus.CALLED_SNAPSHOT)
                tool_trace.append(
                    ToolTraceEntry(
                        adapter=f"Analytics MCP Adapter ({label.value})",
                        status=status,
                        signal_count=len(analytics_signals),
                        note=f"Loaded from snapshot (age: {bundle_snapshot.snapshot_age_minutes:.1f} min)",
                    )
                )

        if analytics_signals is None:
            if self.evidence_mode != EvidenceMode.DEMO:
                tool_trace.append(
                    ToolTraceEntry(
                        adapter="Analytics MCP Adapter (Fallback)",
                        status=TraceStatus.SKIPPED,
                        signal_count=0,
                        note=f"Snapshot for {self.evidence_mode.value} mode unavailable. Falling back to DEMO.",
                    )
                )
            
            analytics_signals = self.analytics_client.get_anomalies()
            tool_trace.append(
                ToolTraceEntry(
                    adapter="Analytics MCP Adapter",
                    status=TraceStatus.CALLED_MOCK,
                    signal_count=len(analytics_signals),
                    note="Loaded from data/analytics_anomalies.json (mock fixture)",
                )
            )

        # Step 2 — Conversations MCP adapter
        conversation_signals = self.conversations_client.get_intent_signals()
        tool_trace.append(
            ToolTraceEntry(
                adapter="Conversations MCP Adapter",
                status=TraceStatus.CALLED_MOCK,
                signal_count=len(conversation_signals),
                note="Loaded from data/conversation_intents.json (mock fixture)",
            )
        )

        # Step 3 — Synthetic Ops adapter
        ops_signals = self.ops_client.get_ops_signals()
        tool_trace.append(
            ToolTraceEntry(
                adapter="Synthetic Ops Adapter",
                status=TraceStatus.CALLED_MOCK,
                signal_count=len(ops_signals),
                note="Loaded from data/commerce_ops_signals.json (mock fixture)",
            )
        )

        # Step 4 — Optional Marketing MCP adapter
        marketing_context = None
        if self.include_marketing:
            marketing_context = self.marketing_client.get_context()
            tool_trace.append(
                ToolTraceEntry(
                    adapter="Marketing MCP Adapter (Optional)",
                    status=TraceStatus.CALLED_MOCK,
                    signal_count=1 if marketing_context else 0,
                    note="No campaign spike in fixture — payment hypothesis not weakened.",
                )
            )
        else:
            tool_trace.append(
                ToolTraceEntry(
                    adapter="Marketing MCP Adapter (Optional)",
                    status=TraceStatus.SKIPPED,
                    signal_count=0,
                    note="Skipped by configuration.",
                )
            )

        # Step 5 — Assemble evidence bundle
        bundle = EvidenceBundle(
            analytics_signals=analytics_signals,
            conversation_signals=conversation_signals,
            ops_signals=ops_signals,
            marketing_context=marketing_context,
        )

        # Step 6 — Score
        score = score_evidence(bundle)

        # Step 7 — Build triage brief
        brief = self.reasoning_engine.build_triage_brief(bundle, score, tool_trace)

        return brief
