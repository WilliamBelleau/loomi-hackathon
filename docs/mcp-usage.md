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

**Authentication:** Browser-based Bloomreach SSO / OIDC.
The first tool call triggers a browser login. After authentication, sessions persist
for **up to 30 days** — subsequent calls in the same session do not re-prompt.

**Programmatic / script-based access:** Not a confirmed Bloomreach-supported pattern.
`scripts/discover_mcp_tools.py` includes an experimental token mode, but this is
not the recommended path. Use an MCP-compatible IDE client for discovery.

**Data access:**
- Tools are **read-only** — no write operations, no customer-facing actions, no ticket creation
- Tools expose live Bloomreach workspace data according to your IAM permissions
- **PII may be masked** depending on your permission level
- **Customer event history is limited to the last 365 days**

**Performance:**
- Ad-hoc analytics queries can take **10–30 seconds** per query
- Rate limits apply; caching applies to repeated identical queries
- For demo reliability, mock adapters are faster and more predictable than live queries

**See also:** `docs/mcp-integration-plan.md` for the full integration audit,
phased plan, and IDE-mediated discovery guidance.

---

## Analytics MCP (Core Demo Candidate)

**File:** `tools/analytics_mcp.py` · Class: `AnalyticsMCPClient`

**Confirmed real MCP capabilities:**
- Project and workspace overview — understand available data structure
- Dashboard and saved funnel inspection — list pre-built analyses
- Ad-hoc analytics queries (EQL-style) — event counts, conversion rates, segment comparisons
- Event schema and property mapping — identify which events and properties are tracked
- Funnel / drop-off analysis — compare steps like add_to_cart vs checkout_start vs purchase
- Channel and region segmentation — where event properties support device type / region filters

**Integration risk:** 🟡 MEDIUM
- Sandbox event property names for channel (mobile/desktop) and region (province) are unconfirmed
- Ad-hoc query latency is 10–30 seconds — mock is faster for demo timing
- Feasibility of the "Quebec / Mobile Web checkout drop" scenario depends on sandbox data

**Current mock:**
- `get_anomalies()` reads `data/analytics_anomalies.json`
- Returns `List[AnalyticsSignal]` with pre-seeded Quebec / Mobile Web checkout drop scenario

**What must be confirmed before Phase D.3 replacement:**
- Sandbox project_id (from Bloomreach sandbox portal — not committed)
- Analytics MCP tool names as confirmed via IDE discovery
- Event property names for device/channel and region segmentation
- Whether sandbox data includes checkout funnel events with sufficient volume
- IAM permissions: what data is visible in the sandbox vs masked

**Swap point:** `AnalyticsMCPClient.get_anomalies()` method body only.
Method signature and return type (`List[AnalyticsSignal]`) do not change.

---

## Marketing MCP (Supporting Context — Optional)

**File:** `tools/marketing_mcp_optional.py` · Class: `MarketingMCPClientOptional`

**Confirmed real MCP capabilities:**
- List active scenarios and their configuration
- List campaigns and campaign calendar entries
- Inspect audience and segment setup
- Check whether any active promotion or campaign could independently explain a conversion change
- Used as a **negative check only**: no active campaign = demand surge is not a plausible explanation
- This adapter is a context source, not an action surface

**Integration risk:** 🟡 MEDIUM
- Already optional in the architecture — scoring runs correctly without it
- Sandbox campaign/scenario data may be sparse or generic

**Current mock:**
- `get_context()` returns a static `MarketingContext` stub with `traffic_spike_detected=False`
- Default fixture: no campaign activity explains the anomaly (supports the payment hypothesis)

**What must be confirmed before Phase D.3 replacement:**
- Marketing MCP tool names as confirmed via IDE discovery
- Whether sandbox has any active scenarios or campaigns that could serve as test context
- Whether traffic attribution data is available for the sandbox project

**Swap point:** `MarketingMCPClientOptional.get_context()` method body only.
Adapter is optional — the orchestrator runs correctly without it.

---

## Conversations MCP (Optional Stretch — Product/Shopping Catalog Only)

**File:** `tools/conversations_mcp.py` · Class: `ConversationsMCPClient`

**Confirmed real MCP role:**
Conversations MCP is a **product/shopping catalog prototype** (Pacific Apparel dataset).

**Confirmed tools:**
- `search_products`
- `search_productCollections`
- `get_product`
- `seeker_products`

**Integration assessment:**
Conversations MCP is confirmed as a product/shopping catalog prototype and does not map
to our current aggregated `payment_failed` intent trend mock. It is a non-fit for the
core demo scenario of aggregated checkout-friction trend analytics.

The mock fixture (`data/conversation_intents.json`) accurately represents the *type* of
signal that *should* come from a customer-voice analytics surface — the architecture is
right; the specific live source for this signal type is a future integration.

**Potential value (stretch only):**
- Product discovery friction examples at the catalog level
- Shopper-intent signals for a product-focused scenario
- Could demonstrate a Simons product-catalog use case if time allows

**Current mock:**
- `get_intent_signals()` reads `data/conversation_intents.json`
- Returns `List[ConversationSignal]` with pre-seeded checkout friction themes
- Mock is clearly labeled; the human review gate ensures no uncorroborated action

**Demo role:** ⚪ **Optional stretch** — Explore only after Analytics and Marketing
discovery is complete and time allows. **Mock is the correct default and demo path.**

**Judge-facing framing:**
> "Conversations MCP is a product discovery surface. For this unified commerce triage
> scenario, the core live MCP path is Analytics + Marketing context, while customer voice /
> checkout-friction signals remain synthetic fixtures unless a suitable live source is confirmed."

---

## Synthetic Ops Adapter (Always Mock — Not a Bloomreach MCP)

**File:** `tools/synthetic_ops.py` · Class: `SyntheticOpsClient`

**Role:**
- Provide payment gateway, OMS, and fulfillment error signals
- Correlate operational errors with analytics signals
- Identify threshold breaches that indicate systemic issues

**This is not a Bloomreach MCP.** It represents internal Simons payment gateway
and OMS data. In a production integration, it would connect to an internal
observability platform (Datadog, Splunk, or equivalent).

**Current mock:**
- `get_ops_signals()` reads `data/commerce_ops_signals.json`
- Returns `List[OpsSignal]` with pre-seeded authorization failure scenario

**Phase 3 path:** Internal ops observability integration — out of scope for this hackathon.

---

## Summary Table

| Adapter | MCP Provider | Status | Demo Role | Phase |
|---|---|---|---|---|
| Analytics MCP | Bloomreach Loomi Connect Analytics | 🟡 Mocked | Core demo candidate | D.3 (blocked on D.2 discovery) |
| Marketing MCP | Bloomreach Loomi Connect Marketing | 🟡 Mocked | Supporting context (optional) | D.3 (blocked on D.2 discovery) |
| Conversations MCP | Bloomreach Loomi Connect Conversations | 🟡 Mocked — confirmed non-fit for core scenario | Optional stretch only | TBD |
| Synthetic Ops | Internal / Observability Platform | 🟡 Mocked (always) | Core mock | Phase 3 |

---

## What We Still Need to Confirm

Authentication is now confirmed (browser SSO — no API key or token required).
What remains before Phase D.3 live adapter work can begin:

1. **Sandbox project URL** — from Bloomreach sandbox portal (never committed to repo)
2. **Analytics MCP tool names** — confirmed via IDE discovery in Antigravity
3. **Event property names** — device/channel and region fields for EQL query segmentation
4. **Sandbox data coverage** — whether the sandbox contains checkout funnel data with
   sufficient volume for the "Quebec / Mobile Web" scenario
5. **IAM permissions** — what data is visible vs PII-masked in the sandbox
6. **Marketing MCP tool names** — confirmed via IDE discovery

Until these details are confirmed through IDE-mediated discovery, all adapters remain
mocked and the demo runs reliably from local fixture data with no external dependencies.

See `docs/antigravity-mcp-test-plan.md` for structured discovery prompts.
