# MCP Usage — Simons Unified Commerce Signal Agent

## Status: Mock-First

All Bloomreach Loomi Connect MCP calls are currently **mocked** using local
synthetic fixture data. No real Bloomreach API credentials, endpoints, tool names,
or schemas are used. This document describes the planned role of each MCP
and what must be replaced once Bloomreach shares sandbox details.

---

## Analytics MCP (Planned)

**File:** `tools/analytics_mcp.py` · Class: `AnalyticsMCPClient`

**Planned role:**
- Detect conversion rate anomalies across funnel steps (browse, add-to-cart, checkout-start, checkout-complete)
- Compare current period metrics against rolling baselines (7-day, 28-day)
- Segment anomalies by channel (Mobile Web, Desktop, App) and region (province, country)
- Surface trend direction and magnitude for triage prioritization
- Identify which funnel steps are affected vs stable (e.g. add-to-cart stable = not demand-driven)

**Current mock:**
- `get_anomalies()` reads `data/analytics_anomalies.json`
- Returns `List[AnalyticsSignal]` with pre-seeded Quebec / Mobile Web checkout drop scenario

**What must be replaced (Phase 2):**
- Obtain Bloomreach Analytics MCP endpoint and authentication method
- Obtain exact tool name (e.g. `loomi_analytics_get_anomalies` — placeholder)
- Obtain request/response schema
- Replace `get_anomalies()` method body with authenticated MCP tool call
- Method signature and return type (`List[AnalyticsSignal]`) do not change

---

## Conversations MCP (Planned)

**File:** `tools/conversations_mcp.py` · Class: `ConversationsMCPClient`

**Planned role:**
- Surface rising customer friction intents from Loomi AI chat interactions
- Identify intent trends by volume spike, channel, and region
- Provide representative customer phrases for each intent cluster
- Correlate intent spikes with analytics anomalies (e.g. payment_failed intent rising = checkout drop is customer-visible)
- Surface emerging intents before they become high-volume (early warning)

**Current mock:**
- `get_intent_signals()` reads `data/conversation_intents.json`
- Returns `List[ConversationSignal]` with pre-seeded payment_failed +42%, cannot_complete_order +38%

**What must be replaced (Phase 2):**
- Obtain Bloomreach Conversations MCP endpoint and authentication method
- Obtain exact tool name and request/response schema
- Replace `get_intent_signals()` method body with authenticated MCP tool call
- Method signature and return type (`List[ConversationSignal]`) do not change

---

## Marketing MCP (Optional, Planned)

**File:** `tools/marketing_mcp_optional.py` · Class: `MarketingMCPClientOptional`

**Planned role:**
- Provide campaign traffic context to avoid false root-cause assumptions
- Identify whether an active campaign could independently explain a conversion anomaly
  (e.g. flash sale driving checkout pressure ≠ payment failure)
- Used to *narrow* the root-cause hypothesis, not to dismiss customer impact
- Signal interpretation:
  - `traffic_spike_detected = False` → demand surge is not a plausible alternative explanation
  - `traffic_spike_detected = True` → weakens confidence in payment/ops root-cause hypothesis only

**Current mock:**
- `get_context()` returns a static `MarketingContext` stub with `traffic_spike_detected=False`
- Default fixture reflects the primary demo scenario: no campaign activity explains the anomaly

**What must be replaced (Phase 2):**
- Obtain Bloomreach Marketing MCP endpoint and authentication method
- Obtain exact tool name and request/response schema
- Replace `get_context()` method body with authenticated MCP tool call
- This adapter is optional — the orchestrator runs without it

---

## Synthetic Ops Adapter (Mock — no real system planned yet)

**File:** `tools/synthetic_ops.py` · Class: `SyntheticOpsClient`

**Role:**
- Provide payment gateway, OMS, and fulfillment error signals
- Correlate operational errors with analytics and conversation signals
- Identify threshold breaches that indicate systemic issues

**Current mock:**
- `get_ops_signals()` reads `data/commerce_ops_signals.json`
- Returns `List[OpsSignal]` with pre-seeded authorization failure scenario

**What must be replaced (Phase 3):**
- Connect to internal Simons payment gateway observability or OMS API
- Or integrate with a unified observability platform (Datadog, Splunk, etc.)
- This is NOT a Bloomreach MCP — it is an internal systems integration

---

## Summary Table

| Adapter | MCP Provider | Status | Phase to Replace |
|---|---|---|---|
| Analytics MCP | Bloomreach Loomi Connect Analytics | 🟡 Mocked | Phase 2 |
| Conversations MCP | Bloomreach Loomi Connect Conversations | 🟡 Mocked | Phase 2 |
| Marketing MCP (Optional) | Bloomreach Loomi Connect Marketing | 🟡 Mocked | Phase 2 |
| Synthetic Ops | Internal / Observability Platform | 🟡 Mocked | Phase 3 |

---

## What We Are Waiting For

To replace any mock adapter with a real call, we need from Bloomreach:

1. **Sandbox environment URL / endpoint**
2. **Authentication method** (API key, OAuth2, MCP session token)
3. **Tool names** for each MCP capability used
4. **Request schema** (what parameters to pass)
5. **Response schema** (what fields to expect, how to page results)
6. **Rate limits and quotas** for the sandbox environment

Until these details are available, all adapters remain mocked and the demo
runs reliably from local fixture data with no external dependencies.
