# MCP Integration Plan — Simons Unified Commerce Signal Agent
## Branch: `mcp-discovery` | Status: Phase D.1 — Discovery Prep

---

## Overview

This document records the MCP integration audit, risks, and phased approach for the
Simons Unified Commerce Signal Agent. It is the authoritative reference for any future
live MCP adapter work.

**Current state:** All adapters are mocked. No network calls exist in the app.
This branch adds discovery infrastructure only — the running application, all mock
adapters, scoring, orchestrator, schemas, tests, and data fixtures are unchanged.

---

## Architecture Framing: MCP as a Read-Only Retrieval Layer

Bloomreach has clarified that Loomi Connect MCP is **read-only** for this hackathon.
This is the correct framing for an agentic decision-support tool.

The architecture operates as a three-layer pipeline:

```
[Retrieval]         →    [Reasoning]          →    [Action Preparation]
MCP tools                Python agent              Human-gated output
(read-only signals)      correlate, score,         TriageBrief + draft note
                         rank, hypothesize         no auto-action, no write
```

**The MCP layer fetches context.** It does not decide.
**The agent correlates.** Cross-source scoring, confidence weighting, root-cause hypothesis.
**The human acts.** The triage brief is a recommendation artifact, not an execution trigger.

### Judge-Facing Framing

> "Loomi Connect MCP is a read-only contextual intelligence layer. It retrieves signals;
> the agent correlates, scores, and prepares a triage artifact; a human reviews before any
> action is taken. The agent's job is comprehension and synthesis, not automation."

### Why the Reasoning Layer Is Non-Trivial Even With Read-Only MCP

1. **Cross-source signal correlation** — Analytics + Conversations + Ops each surface an
   independent signal. The agent is the first system to ask: *do all three point at the
   same root cause?*
2. **Transparent confidence scoring** — Not just "anomaly detected" but "confidence 0.90
   because three independent sources corroborate and no alternative explanation is present."
   Every point is traceable to a named signal.
3. **Hypothesis elimination** — The Marketing MCP check rules out a demand-surge alternative
   explanation before the payment-path hypothesis is recommended. Dashboards do not do this.
4. **Draft artifact preparation** — The Jira-style incident note is ready for a human to
   validate and file. MCP retrieval alone cannot produce this structured output.

### Why Human Review Is Architecturally Correct, Not Just Cosmetically Safe

Read-only MCP means the agent has no write access to Bloomreach, to ticketing systems,
or to internal ops tools. The human review gate is not a safety disclaimer added at the
end — it is the only possible final step. Frame this as intentional design:

> "The agent compresses 45 minutes of manual signal correlation into seconds of structured
> evidence. What a human does with that evidence is the human's decision."

---

## MCP Mapping Matrix

### Analytics MCP

| Dimension | Detail |
|---|---|
| **Current mock method** | `AnalyticsMCPClient.get_anomalies()` → `List[AnalyticsSignal]` |
| **Likely real MCP role** | Ad-hoc EQL-style analytics queries: conversion funnel metrics, segment breakdowns, anomaly detection over rolling windows |
| **Expected input** | Query parameters: metric name(s), date range, segment filters (channel, region), comparison period |
| **Expected output** | Metric values, delta vs baseline, segment labels — maps to existing `AnalyticsSignal` fields |
| **Integration risk** | 🟡 MEDIUM — EQL query syntax is unknown; tool name is unknown; sandbox data coverage is unknown |
| **Fallback behavior** | Returns fixture data from `data/analytics_anomalies.json` (current default, unchanged) |
| **Demo role** | ✅ **Core demo** — Highest-confidence integration candidate; pursue first |
| **Swap point** | `AnalyticsMCPClient.get_anomalies()` method body only; signature and return type do not change |

### Conversations MCP

| Dimension | Detail |
|---|---|
| **Current mock method** | `ConversationsMCPClient.get_intent_signals()` → `List[ConversationSignal]` |
| **Likely real MCP role** | **Under validation.** May surface customer session signals and checkout friction themes from Loomi chat interactions. May be product/shopping-oriented rather than aggregated support-intent analytics. |
| **Expected input** | TBD — possibly: session ID, date range, customer segment |
| **Expected output** | TBD — session-level signals or aggregated intent themes; aggregated trend data (spike %) is not confirmed |
| **Integration risk** | 🔴 HIGH — See Conversations MCP Risk Assessment below |
| **Fallback behavior** | Returns fixture data from `data/conversation_intents.json` (current default, unchanged) |
| **Demo role** | ⚠️ **Core mock, optional live** — Keep in story as clearly labeled mock; do not block demo on live validation |
| **Swap point** | `ConversationsMCPClient.get_intent_signals()` method body only; pending schema confirmation |

### Marketing MCP (Optional)

| Dimension | Detail |
|---|---|
| **Current mock method** | `MarketingMCPClientOptional.get_context()` → `MarketingContext` |
| **Likely real MCP role** | Campaign context retrieval: active campaigns, traffic attribution, audience segment activity — used as a negative check (no spike = payment hypothesis not weakened) |
| **Expected input** | Date range, segment filter, optional campaign ID |
| **Expected output** | Campaign name, traffic volume delta, active flag — maps to existing `MarketingContext` fields |
| **Integration risk** | 🟡 MEDIUM — Already optional in architecture; scoring runs correctly without it |
| **Fallback behavior** | Orchestrator runs with `include_marketing=False` (already implemented) |
| **Demo role** | 🟢 **Stretch** — Nice-to-have if schema confirmed; not required for core story |
| **Swap point** | `MarketingMCPClientOptional.get_context()` method body only |

### Synthetic Ops Adapter (Not a Bloomreach MCP)

| Dimension | Detail |
|---|---|
| **Current mock method** | `SyntheticOpsClient.get_ops_signals()` → `List[OpsSignal]` |
| **Real role** | Internal Simons payment gateway / OMS data — NOT a Bloomreach MCP (confirmed in `docs/mcp-usage.md`) |
| **Integration risk** | ✅ LOW — Correctly labeled as synthetic; no MCP integration planned for hackathon |
| **Fallback behavior** | Always returns fixture data; this is the correct behavior for all demo phases |
| **Demo role** | ✅ **Core mock** — Essential for 3-source corroboration story; always labeled synthetic |
| **Phase 3 path** | Internal ops observability integration (Datadog, Splunk, or equivalent) |

---

## Conversations MCP Risk Assessment

### The Risk

The current mock returns **aggregated intent trend data** — specifically, `payment_failed`
intent volume up 42% and `cannot_complete_order` intent up 38% across a time window, with
representative customer phrases.

This presupposes that the Conversations MCP provides:
- Historical intent aggregation (not just per-session lookups)
- Intent trend analysis (spike detection, volume comparison vs baseline)
- Structured intent taxonomy with named intents like `payment_failed`

Bloomreach has indicated the Conversations MCP is "product/shopping-oriented." This
suggests it may surface:
- Product recommendations from Loomi chat sessions
- Per-session conversation context and Q&A content
- Shopping intent classification per interaction

These are per-session, product-catalog signals — not aggregated friction-intent trends.

### Assessment: **Moderate-to-high risk of schema mismatch.**

### Safe Reframing (in effect for all documentation and UI)

**Avoid claiming:** "aggregated customer friction intent trends — payment_failed ↑42%"

**Use instead:** "customer session signals — checkout friction themes surfaced from recent
Loomi chat interactions"

This framing:
- Is defensible even if Conversations MCP returns session-level data rather than trends
- Remains accurate for the mock fixture (which does describe friction themes)
- Does not overclaim an aggregated analytics capability that may not exist

### Fallback If Schema Mismatch Is Confirmed

If the discovery script shows Conversations MCP has no intent-trend aggregation tool:
- Update the tool trace note to: "Schema validation pending — using mock fallback"
- Add this to the demo script as an explicit honest talking point
- The agent "knowing what it doesn't know" is itself a responsible design story

---

## Loomi Connect MCP Transport Notes

Based on official hackathon documentation:

- **Transport:** Streamable HTTP (not stdio MCP)
- **Authentication:** Browser-based Bloomreach authentication through supported MCP clients
- **Programmatic access:** Token-based access for scripts/tools is **TBD / under validation**.
  Do not assume API-key style auth. Do not assume token auth works without browser-auth flow.
- **Access mode:** Read-only for this hackathon

The discovery script (`scripts/discover_mcp_tools.py`) is designed to handle the
uncertainty in programmatic auth — it will fail safely with a clear message if the
configured auth mode does not permit tool listing.

---

## Phased Implementation Plan

### Phase D.1 — Discovery Prep (Current — this branch)

**Goal:** Add discovery infrastructure without changing the running application.

**Changes:**
- ✅ `docs/mcp-integration-plan.md` — this document
- ✅ `.env.example` — add transport and feature-flag variables (commented out)
- ✅ `.gitignore` — add discovery output exclusions
- ✅ `docs/mcp-usage.md` — add transport section, Conversations reframe
- ✅ `scripts/discover_mcp_tools.py` — standalone discovery helper

**Unchanged:** `agent/`, `tools/`, `app/`, `data/`, `tests/`, all schemas, all adapters.

### Phase D.2 — After Schema Confirmation (Blocked on discovery)

Prerequisites: discovery script confirms real tool names and schemas.

**Planned changes (not yet approved):**
- Add `tools/analytics_mcp_live.py` — feature-flagged live adapter
- Orchestrator reads `LOOMI_MCP_LIVE=true` and swaps client
- Existing mock adapter and all tests unchanged
- Save discovery output JSON locally as reference snapshot (gitignored, not committed)

### Phase D.3 — Demo Day Decision

- If live Analytics MCP is stable on sandbox: run with `LOOMI_MCP_LIVE=true` locally
- If any instability: demo with mock; show discovery output as evidence of real exploration
- Either path is a complete, honest demo

---

## Pre-Demo Verification Checklist

- `python -m pytest -v` → 49/49 green (no app changes, tests must always pass)
- `python -m streamlit run app/ui_streamlit.py` → loads without any network calls
- `LOOMI_MCP_LIVE` is not set or is `false` → mock path confirmed active
- `git grep -n "LOOMI_MCP_TOKEN\|LOOMI_MCP_URL\|LOOMI_MCP_ANALYTICS_MARKETING_URL\|LOOMI_MCP_CONVERSATIONS_URL" .` → only `.env.example` matches

---

*Phase D.1 complete. Phase D.2 blocked pending discovery script results.*
