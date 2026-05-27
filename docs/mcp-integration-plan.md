# MCP Integration Plan — Simons Unified Commerce Signal Agent
## Status: Phase D.1 Complete — Phase D.2 Blocked on IDE-Mediated Discovery

---

## Overview

This document is the authoritative reference for MCP integration strategy. It reflects
confirmed facts from the official Bloomreach Loomi Connect documentation.

**Current state:** All adapters are mocked. No network calls exist in the app.
Phase D.1 added discovery infrastructure — the running application, all mock adapters,
scoring, orchestrator, schemas, tests, and data fixtures are unchanged.

**Phase D.2** is blocked on completing IDE-mediated discovery (see below) to confirm
Analytics and Marketing MCP tool names, input schemas, and sandbox data feasibility.

---

## Architecture Framing: MCP as a Read-Only Intelligence Layer

Loomi Connect MCP is a **read-only** retrieval layer. This is the correct framing for
an agentic decision-support tool.

The architecture operates as a three-layer pipeline:

```
[Retrieval]            →    [Reasoning]           →    [Action Preparation]
Loomi Connect MCP           Python agent               Human-gated output
(read-only signals)         correlate, score,          TriageBrief + draft note
                            rank, hypothesize          no auto-action, no write
```

**The MCP layer retrieves context.** It does not decide.
**The agent correlates.** Cross-source scoring, confidence weighting, root-cause hypothesis.
**The human acts.** The triage brief is a recommendation artifact, not an execution trigger.

### Judge-Facing Framing

> "Loomi Connect MCP is the read-only intelligence layer. The agent uses it to retrieve
> context, then performs cross-signal correlation, confidence scoring, and draft incident
> preparation. Business-impacting action stays human-reviewed and simulated."

### Why the Reasoning Layer Is Non-Trivial Even With Read-Only MCP

1. **Cross-source signal correlation** — Analytics + Marketing + Ops each surface an
   independent signal. The agent asks: *do all signals point at the same root cause?*
2. **Transparent confidence scoring** — Not just "anomaly detected" but "confidence 0.90
   because three independent sources corroborate and no alternative explanation is present."
   Every point is traceable to a named signal.
3. **Hypothesis elimination** — The Marketing MCP check rules out a demand-surge alternative
   explanation before the payment-path hypothesis is recommended.
4. **Draft artifact preparation** — The Jira-style incident note is ready for a human to
   validate and file. MCP retrieval alone cannot produce this structured output.

### Why Human Review Is Architecturally Correct, Not Just Cosmetically Safe

Read-only MCP means the agent has no write access to Bloomreach, to ticketing systems,
or to internal ops tools. The human review gate is not a safety disclaimer — it is the
only possible final step. Frame this as intentional design:

> "The agent compresses 45 minutes of manual signal correlation into seconds of structured
> evidence. What a human does with that evidence is the human's decision."

---

## Confirmed Transport and Authentication Facts

From the official Bloomreach Loomi Connect documentation:

| Property | Confirmed Value |
|---|---|
| **Transport** | Streamable HTTP (remote MCP server, not stdio) |
| **Integration method** | MCP — the only supported integration method |
| **Normal client** | MCP-compatible AI application: Antigravity, Claude Code, Cursor, VS Code with MCP extension |
| **Authentication** | Browser-based Bloomreach SSO / OIDC — no API keys, no custom headers required |
| **Auth trigger** | First tool call triggers browser login |
| **Session lifetime** | Up to 30 days |
| **Access mode** | Read-only |
| **Data exposure** | Live workspace data, according to IAM permissions |
| **PII** | May be masked depending on permission level |
| **Event history window** | Last 365 days |
| **Ad-hoc analytics latency** | 10–30 seconds per query |
| **Rate limits** | Apply — caching also applies to repeated queries |

### Recommended Discovery Path: IDE-Mediated via Antigravity

The Bloomreach-supported path for discovering and exploring MCP tools is:

1. Configure the Loomi MCP server URL in an MCP-compatible IDE client
   (Antigravity, Claude Code, Cursor, or VS Code with MCP extension).
2. Authenticate via browser SSO when prompted on the first tool call.
3. Use the IDE's native MCP tool browser or prompt the AI assistant to
   list and explore available tools.
4. Record confirmed tool names and schemas in this document.

**See `docs/antigravity-mcp-test-plan.md`** for structured test prompts and
output capture guidance.

### Python / Programmatic Discovery: Experimental — Not Recommended

Token-based or script-based programmatic access to Loomi Connect MCP is **not a
confirmed Bloomreach-supported pattern**. The official docs describe no API key or
custom header mechanism for direct programmatic access.

`scripts/discover_mcp_tools.py` retains an experimental token mode for completeness,
but this is not the recommended path. Use IDE-mediated discovery first.

---

## MCP Mapping Matrix

### Analytics MCP

| Dimension | Detail |
|---|---|
| **Current mock method** | `AnalyticsMCPClient.get_anomalies()` → `List[AnalyticsSignal]` |
| **Confirmed real MCP capabilities** | Project and workspace overview; dashboards and saved funnels; ad-hoc analytics queries (EQL-style); event schema and property mapping; funnel/drop-off analysis; channel and region segmentation where event properties support it |
| **Expected input** | Project ID, event names, date range, property filters; exact query syntax confirmed via IDE discovery |
| **Expected output** | Metric values, event counts, funnel steps, segment breakdowns — maps to `AnalyticsSignal` fields if event properties support channel/region |
| **Integration risk** | 🟡 MEDIUM — Sandbox data coverage and event property names unconfirmed; ad-hoc queries take 10–30 seconds |
| **Fallback behavior** | Returns fixture data from `data/analytics_anomalies.json` (current default, unchanged) |
| **Demo role** | ✅ **Core demo candidate** — Pursue first; depends on sandbox data feasibility |
| **Swap point** | `AnalyticsMCPClient.get_anomalies()` method body only; signature and return type do not change |

### Marketing MCP (Optional)

| Dimension | Detail |
|---|---|
| **Current mock method** | `MarketingMCPClientOptional.get_context()` → `MarketingContext` |
| **Confirmed real MCP capabilities** | List active scenarios; list campaigns; inspect audience/segment setup; campaign calendar and context; used to determine whether any active promotion could explain a conversion change |
| **Expected input** | Project ID, date range; exact query syntax confirmed via IDE discovery |
| **Expected output** | Active scenarios, campaign names, traffic context — maps to `MarketingContext` fields |
| **Integration risk** | 🟡 MEDIUM — Already optional in architecture; scoring runs correctly without it |
| **Fallback behavior** | Orchestrator runs with `include_marketing=False` (already implemented) |
| **Demo role** | 🟢 **Supporting context** — Used as a negative check: no active campaign = demand surge is not a plausible explanation |
| **Swap point** | `MarketingMCPClientOptional.get_context()` method body only |

### Conversations MCP

| Dimension | Detail |
|---|---|
| **Current mock method** | `ConversationsMCPClient.get_intent_signals()` → `List[ConversationSignal]` |
| **Confirmed real MCP role** | Product/shopping catalog prototype against Pacific Apparel dataset |
| **Confirmed tools** | `search_products`, `search_productCollections`, `get_product`, `seeker_products` |
| **Integration assessment** | **Confirmed non-fit for aggregated checkout-friction trend analytics.** This MCP surfaces product discovery signals, not aggregated payment-intent trends or support-intent spikes. |
| **Potential value** | Product discovery friction examples; shopper-intent context at catalog level; could illustrate a product-side scenario if time allows |
| **Fallback behavior** | Returns fixture data from `data/conversation_intents.json` — mock is the correct default |
| **Demo role** | ⚪ **Optional stretch** — Explore only after Analytics and Marketing discovery is complete and time allows |
| **Swap point** | Not applicable for current demo scenario; would require a different `ConversationSignal` framing |

**Judge-facing framing:**
> "Conversations MCP is a product discovery surface. For this unified commerce triage
> scenario, the core live MCP path is Analytics + Marketing context, while customer voice /
> checkout-friction signals remain synthetic fixtures unless a suitable live source is confirmed."

### Synthetic Ops Adapter

| Dimension | Detail |
|---|---|
| **Current mock method** | `SyntheticOpsClient.get_ops_signals()` → `List[OpsSignal]` |
| **Real role** | Internal Simons payment gateway / OMS / fulfillment data — NOT a Bloomreach MCP |
| **Integration risk** | ✅ LOW — Correctly labeled as synthetic; no MCP integration planned for hackathon |
| **Fallback behavior** | Always returns fixture data — this is the correct behavior |
| **Demo role** | ✅ **Core mock** — Essential for 3-source corroboration story; always labeled synthetic |
| **Phase 3 path** | Internal ops observability integration (Datadog, Splunk, or equivalent) |

---

## Conversations MCP — Confirmed Assessment

The current mock returns **aggregated intent trend data**: `payment_failed` intent volume
up 42%, `cannot_complete_order` up 38% across a time window, with representative phrases.

The official Bloomreach docs confirm that Conversations MCP is a **product/shopping catalog
prototype** (Pacific Apparel dataset) with tools focused on product search and discovery.

**Internal technical summary:**
Conversations MCP is confirmed as a product/shopping catalog prototype and does not map
to our current aggregated `payment_failed` intent trend mock. It is a non-fit for the
core demo scenario.

**What this means for the demo:**
- Mock is correct and honest — always was
- The mock fixture (`data/conversation_intents.json`) accurately represents what
  *should* come from a customer-voice analytics surface — we just don't have that
  live MCP surface yet
- This is a clear, defensible story: the agent architecture is right; the specific
  live source for this signal type is TBD

**Fallback framing for judges:**
Conversations signals remain synthetic fixtures. The agent correctly labels them as mock
and the human review gate ensures no action is taken on uncorroborated signals.

---

## Phase D.2 — IDE-Mediated Discovery (Current Blocker)

**Goal:** Confirm Analytics and Marketing MCP tool names and sandbox data feasibility
before writing any live adapter code.

**Method:** IDE-mediated discovery via Antigravity or another supported MCP client.
See `docs/antigravity-mcp-test-plan.md` for structured test prompts.

**Prerequisites to unblock Phase D.3:**
- Sandbox project URL configured in IDE (not committed to repo)
- Analytics MCP: confirm tool names, event property names for channel/region, feasibility
  of the checkout funnel scenario against sandbox data
- Marketing MCP: confirm scenario/campaign tool names, confirm negative-check capability
- Document confirmed findings in this file

**Phase D.3 — Live Adapter (Blocked on D.2)**

Prerequisites: IDE discovery confirms tool names and sandbox scenario feasibility.

Planned changes (not yet approved):
- Add `tools/analytics_mcp_live.py` — feature-flagged live adapter (Analytics only)
- Orchestrator reads `LOOMI_MCP_LIVE=true` and swaps client
- Existing mock adapter and all 49 tests unchanged
- Conversations and Ops remain mock — confirmed appropriate for demo

---

## Pre-Demo Verification Checklist

- `python -m pytest -v` → 49/49 green (no app changes; tests must always pass)
- `python -m streamlit run app/ui_streamlit.py` → loads without any network calls
- `LOOMI_MCP_LIVE` is not set or is `false` → mock path confirmed active
- Ad-hoc queries 10–30 seconds: demo from mock for reliable timing
- `git grep -n "LOOMI_MCP_ANALYTICS_MARKETING_URL\|LOOMI_MCP_CONVERSATIONS_URL" .`
  → only `.env.example` matches (no values committed)

---

*Phase D.1 complete. Phase D.2 requires IDE-mediated discovery — see `docs/antigravity-mcp-test-plan.md`.*
