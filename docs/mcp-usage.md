# MCP Usage — Simons Unified Commerce Signal Agent

## Status: Mock-First

All Bloomreach Loomi Connect MCP calls are currently **mocked** using local
synthetic fixture data. No real Bloomreach API credentials, endpoints, tool names,
or schemas are used. This document describes the planned role of each MCP
and what must be replaced once Bloomreach shares sandbox details.

---

## Transport and Authentication

**Transport:** Bloomreach Loomi Connect MCP uses **Streamable HTTP** transport
(not stdio MCP). This is a remote MCP server accessed over HTTPS.

**Authentication:** The official integration path uses **browser-based Bloomreach
authentication** through supported MCP clients (e.g., Claude Desktop, Cursor).
This means a human authenticates in a browser session; the MCP client then holds
the session context.

**Programmatic access:** Token-based programmatic access (for standalone scripts
or server-side Python) is **TBD and pending confirmation** from Bloomreach.
Do not assume token auth works without testing. The discovery script
(`scripts/discover_mcp_tools.py`) is designed to handle this uncertainty and
will exit gracefully if programmatic auth is not available.

**Read-only:** All Loomi Connect MCP tools are read-only for this hackathon.
No write operations, no customer-facing actions, no ticket creation via MCP.

**See also:** `docs/mcp-integration-plan.md` for the full integration audit and
phased implementation plan.

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

## Conversations MCP (Pending Schema Validation)

**File:** `tools/conversations_mcp.py` · Class: `ConversationsMCPClient`

**Planned role (pending confirmation):**
- Surface customer session signals and checkout friction themes from Loomi AI chat interactions
- Provide context on what customers are struggling with during shopping and checkout flows
- Correlate session-level friction themes with analytics anomalies (e.g., payment issues
  surfacing in chat confirm that the checkout drop is customer-visible)
- Intent taxonomy, aggregation method, and spike-detection capability are **not yet confirmed**

> **Schema validation status: PENDING.**
> Bloomreach has indicated Conversations MCP is product/shopping-oriented.
> Aggregated intent trend data (e.g., spike percentages across a time window) may not be
> directly available. Live Conversations MCP mapping is blocked on discovery script results.
> The safe description is: *customer session signals — checkout friction themes surfaced
> from recent Loomi chat interactions.*

**Current mock:**
- `get_intent_signals()` reads `data/conversation_intents.json`
- Returns `List[ConversationSignal]` with pre-seeded payment_failed and cannot_complete_order
  friction themes (described as session signals, not confirmed aggregated trend spikes)

**What must be confirmed before Phase 2 replacement:**
- Whether Conversations MCP exposes aggregated intent trend data or per-session signals
- Exact tool name and request/response schema
- Whether `ConversationSignal.spike_pct` can be populated from real data or must be reframed
- Method signature and return type (`List[ConversationSignal]`) may need adjustment
  depending on real schema

**Fallback if schema mismatch confirmed:**
- Tool trace note updated to: "Schema validation pending — using mock fallback"
- Conversations remains in the demo story as an honest labeled mock

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

| Adapter | MCP Provider | Status | Demo Role | Phase to Replace |
|---|---|---|---|---|
| Analytics MCP | Bloomreach Loomi Connect Analytics | 🟡 Mocked | Core demo | Phase 2 |
| Conversations MCP | Bloomreach Loomi Connect Conversations | 🟡 Mocked — schema pending | Core mock, optional live | Phase 2 (blocked on schema) |
| Marketing MCP (Optional) | Bloomreach Loomi Connect Marketing | 🟡 Mocked | Stretch | Phase 2 |
| Synthetic Ops | Internal / Observability Platform | 🟡 Mocked (always) | Core mock | Phase 3 |

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
