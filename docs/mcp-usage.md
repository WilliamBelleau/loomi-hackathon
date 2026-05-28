# MCP Usage — Simons Unified Commerce Signal Agent

## Status: Mock-First

All Bloomreach Loomi Connect MCP calls are currently **mocked** using local
synthetic fixture data. No real Bloomreach credentials, endpoint values, tool names,
or schemas are committed to this repository. This document describes the confirmed and
planned role of each MCP adapter and what must be completed before live replacement.

---

## Transport and Authentication

From the official Bloomreach Loomi Connect documentation:

**Transport:** Streamable HTTP — a remote MCP server accessed over HTTPS.
This is not stdio MCP. The server is hosted by Bloomreach; clients connect over the network.

**Normal setup:** Configure the MCP server URL in a supported MCP-compatible AI application:
- Antigravity (recommended for this project)
- Claude Code
- Cursor
- VS Code with MCP extension

No API keys, tokens, or custom headers are required for normal MCP use.
# Bloomreach Loomi Connect MCP Usage

This document details how the Simons Unified Commerce Signal Agent connects to Bloomreach Loomi Connect via the Model Context Protocol (MCP).

## True Live Loomi MCP Integration

The agent now features true Live Loomi MCP integration. 
- Streamlit can call Loomi Connect MCP through `mcp-remote` via stdio client wrapper.
- Uses `execute_analytics_eql` to pull aggregated checkout, cart, funnel, and campaign signals.
- Normalizes the response directly into the triage agent using the `LiveEvidenceBundle`.

### Execution Modes & Cache Strategy
- **Live Loomi MCP Mode**: Connects live.
- **Cache Fallback (Last Successful MCP Refresh)**: Protects demo reliability if authentication or rate limits fail. It is a fallback only, not the primary live path.
- **Demo Fixture Mode**: Uses purely synthetic mock data for guaranteed narrative delivery.

---

## Adapter Summary Table

| Adapter | Role | Status | Source |
|---|---|---|---|
| **Analytics MCP** | Core Funnel & Checkout metrics | **Live** | Bloomreach Loomi Connect (`execute_analytics_eql`) |
| **Marketing MCP** | Campaign traffic correlation | **Live** | Bloomreach Loomi Connect |
| **Conversations MCP** | Customer intent signals | **Synthetic** | Mock Fixture (Real MCP is for product catalog) |
| **Synthetic Ops** | Payment gateway, OMS, fulfillment errors | **Synthetic** | Mock Fixture (Simons internal systems) |

---

## Analytics MCP (Live Core)

**Files:** `tools/live_mcp_client.py` & `tools/live_evidence_adapter.py`
**Fallback:** `tools/analytics_mcp.py`

**Real MCP capabilities utilized:**
- Ad-hoc analytics queries (EQL)
- Funnel and drop-off analysis
- Conversion rates and session trends

The live adapter connects to `loomi-mcp-alpha.bloomreach.com/mcp` and executes Bloomreach EQL.
It maps the JSON payload into an internal `LiveEvidenceBundle`, which the orchestrator consumes to generate the triage brief.

---

## Marketing MCP (Live Supporting Context)

**Files:** Reuses live client via `tools/live_evidence_adapter.py`
**Fallback:** `tools/marketing_mcp_optional.py`

**Real MCP capabilities utilized:**
- Detect active campaigns
- Negative correlation check (no active campaign = demand surge is not a plausible explanation for payment failure)

---

## Conversations MCP (Optional Stretch – Synthetic)

**File:** `tools/conversations_mcp.py`

**Role:**
The actual Conversations MCP focuses on product catalog discovery (e.g. Pacific Apparel), which is a non-fit for the core payment-friction analytics demo. Thus, the Conversations MCP adapter uses synthetic fixture data (`data/conversation_intents.json`) to accurately represent the type of customer-voice signal ("payment failed") that a triage agent needs.

**Demo role:** Optional stretch. For the triage scenario, the core live MCP path is Analytics + Marketing context.

---

## Synthetic Ops Adapter (Synthetic – Non-Bloomreach)

**File:** `tools/synthetic_ops.py`

**Role:**
Provides payment gateway, OMS, and fulfillment error signals. These operational signals **do not exist in the Bloomreach sandbox** and would come from a retailer's internal commerce systems (e.g., Datadog, Splunk).

This is intentionally synthetic to demonstrate how Bloomreach signals are correlated with external enterprise systems to uncover the root cause.
