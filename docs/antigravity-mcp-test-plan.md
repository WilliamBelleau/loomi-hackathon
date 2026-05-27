# Antigravity MCP Test Plan — Simons Unified Commerce Signal Agent
## IDE-Mediated Loomi Connect MCP Discovery Guide

---

## Purpose and Scope

This document guides safe, structured exploration of Bloomreach Loomi Connect MCP tools
from within an MCP-compatible IDE client (Antigravity recommended).

**What this achieves:**
- Confirms real Analytics and Marketing MCP tool names and schemas
- Determines whether the sandbox can support the "Quebec / Mobile Web checkout drop" scenario
- Provides a basis for Phase D.3 live adapter decisions

**What this does NOT do:**
- The Streamlit app remains mock-first throughout
- No live MCP calls are added to the app
- No credentials are committed to the repo
- No real customer PII is captured or stored

---

## Setup — No Credentials in Repo

Configure the Loomi MCP server in your IDE client settings, **not** in any committed file.

1. Obtain the MCP server URL(s) from the Bloomreach sandbox portal or hackathon Slack.
2. In Antigravity (or your MCP client): add the MCP server URL to your local MCP configuration.
   - Analytics / Marketing URL → one MCP server
   - Conversations URL → a separate MCP server
3. On the first tool call, browser-based Bloomreach SSO / OIDC triggers automatically.
   No API key, token, or custom header is needed.
4. Sessions persist for up to 30 days. Subsequent calls in the same session do not re-prompt.

> **Never add the MCP server URL as an environment variable in `.env` with a real value.**
> The `.env` file is gitignored but any mistaken `git add` of a filled `.env.example` would
> expose the endpoint. Keep the URL in your IDE's local settings only.

---

## What to Capture — and What Not to Capture

### ✅ Safe to capture and document

| Item | Where to record |
|---|---|
| Confirmed tool names (e.g., `get_project_overview`) | `docs/mcp-integration-plan.md` |
| Input schema key names (not values) | `docs/mcp-integration-plan.md` |
| Output field names (not data values) | `docs/mcp-integration-plan.md` |
| Event names that exist in sandbox (e.g., `checkout`, `purchase`) | `docs/mcp-integration-plan.md` |
| Property names for channel, device, region segmentation | `docs/mcp-integration-plan.md` |
| Whether the sandbox scenario is feasible (yes/no + rationale) | `docs/mcp-integration-plan.md` |

### ❌ Do not capture or commit

| Item | Reason |
|---|---|
| Real customer names, email addresses, order IDs | PII — may be unmasked in sandbox |
| Raw MCP response payloads containing customer data | PII risk even if data is synthetic |
| MCP server endpoint URLs | Must not appear in committed files |
| Browser session cookies or auth tokens | Credentials |
| Screenshots showing endpoint URLs, customer data, or raw responses | PII + credential risk |
| Any data about real Bloomreach customers or real Simons customers | Never in this repo |

> **If a response contains visible PII:** Note that the field exists and its name.
> Do not copy the value. Note whether IAM masking was applied.

---

## Phase A — Workspace Orientation

Run these prompts after connecting to the Analytics / Marketing MCP server.

**Goal:** Understand the available workspace structure and identify the sandbox project.

### Prompt sequence

```
List the Bloomreach organizations I have access to.
```

```
List workspaces and projects for the sandbox organization.
```

```
What is the project_id for the hackathon sandbox project?
```

### What to record

- Project ID for the sandbox (needed for all subsequent queries)
- Whether multiple projects exist and which to use
- Any IAM restrictions visible in the response

---

## Phase B — Project and Data Model

**Goal:** Understand the event schema and property structure before running analytics queries.

### Prompt sequence

```
Get the project overview for the sandbox project [project_id].
```

```
Get the customer schema for this project — what customer properties are tracked?
```

```
Get the event schema — what event types are tracked in this project?
```

```
Get the project mapping — what properties are indexed and available for filtering?
```

```
Do any of these event types exist in the project:
add_to_cart, checkout_start, checkout_complete, purchase, page_visit, search?
```

```
Do events have a device type or channel property (e.g., mobile_web, desktop)?
```

```
Do events have a region or province property (e.g., Quebec, Ontario)?
```

### What to record

- Confirmed event names for checkout funnel steps
- Property name for device/channel (e.g., `device_type`, `channel`, `platform`)
- Property name for region/province (e.g., `region`, `province`, `geo_country`)
- Whether the sandbox has sufficient data to demonstrate a checkout funnel analysis

> **Feasibility question:** Can the sandbox support the mock scenario
> "mobile checkout friction affecting Quebec customers"?
> Record: yes / partially / no, with property names that do or don't exist.

---

## Phase C — Analytics Feasibility

**Goal:** Determine whether the Analytics MCP can produce signals comparable to the mock.

> **Note:** Ad-hoc analytics queries can take 10–30 seconds. This is expected behavior.
> Do not retry immediately if a query is slow.

### Prompt sequence

```
List available dashboards and saved funnels for this project.
```

```
Run an ad-hoc query: count add_to_cart events and checkout_start events
over the last 30 days. Compare the two.
```

```
If device type is available: break down checkout_start events by device type
over the last 7 days.
```

```
If region is available: break down checkout_start events by region
over the last 7 days.
```

```
Can you identify a period where checkout_start conversion dropped
compared to the 7-day baseline? (This may not be possible if sandbox data is sparse.)
```

### What to record

- Whether saved funnels or dashboards exist
- Whether ad-hoc funnel queries work (yes/no + example tool name used)
- Whether device/channel segmentation is possible from event properties
- Whether region segmentation is possible
- Overall feasibility verdict: **Full / Partial / Not feasible** for the demo scenario

---

## Phase D — Marketing Context Feasibility

**Goal:** Confirm whether Marketing MCP can provide the negative campaign-context check.

### Prompt sequence

```
List active scenarios for this project.
```

```
List active campaigns or campaign calendar entries for this project.
```

```
Is there any active campaign or scenario that could explain a
conversion rate change in the last 7 days?
```

```
If a campaign exists: what audience segment does it target?
Does it include mobile web users or Quebec customers?
```

### What to record

- Whether scenarios and campaigns are listed by Marketing MCP
- Tool names used (e.g., `list_scenarios`, `get_campaigns`)
- Whether the negative-check use case works: "no active campaign → demand surge is not the cause"
- Feasibility verdict for Marketing MCP integration

---

## Phase E — Conversations MCP Confirmation

**Goal:** Confirm that Conversations MCP is a product catalog tool and decide whether to
pursue as optional stretch.

Connect to the Conversations MCP server URL separately before running these prompts.

### Prompt sequence

```
What tools are available from this MCP server?
```

```
Search for products related to the term "checkout". What results come back?
```

```
Search for product collections. What types of collections exist?
```

```
Is this tool working against a product catalog?
What dataset or brand does it appear to use?
```

### Expected findings

- Confirmed tools: `search_products`, `search_productCollections`, `get_product`, `seeker_products`
- Pacific Apparel product catalog dataset
- Product discovery / shopping search — not support intent analytics

### Decision point

| Finding | Decision |
|---|---|
| Confirms Pacific Apparel catalog, product search tools only | Keep Conversations as optional stretch. Mock remains the correct demo path. |
| Finds unexpected intent-trend or analytics tools | Document and reassess |
| Server unavailable or returns errors | Note in plan; mock remains default |

### What to record

- Confirmed tool names from Conversations MCP
- Dataset or brand confirmed (Pacific Apparel)
- Final decision: optional stretch / not applicable for core demo

---

## Adapter Mapping Table — Mock vs Real MCP

Use this table to record findings from IDE discovery.

| Mock Adapter | Mock Method | Real MCP Candidate | Feasibility | Notes |
|---|---|---|---|---|
| `AnalyticsMCPClient` | `get_anomalies()` | Analytics MCP ad-hoc query tool | **TBD — confirm in Phase C** | Depends on sandbox event schema |
| `ConversationsMCPClient` | `get_intent_signals()` | Conversations MCP | **Confirmed non-fit** | Pacific Apparel catalog; keep mock |
| `MarketingMCPClientOptional` | `get_context()` | Marketing MCP scenario/campaign tool | **TBD — confirm in Phase D** | Negative-check use case |
| `SyntheticOpsClient` | `get_ops_signals()` | No Bloomreach MCP equivalent | **Always mock** | Internal ops data; Phase 3 |

---

## After Discovery — What to Do With Findings

### If Analytics MCP can support the demo scenario

1. Update `docs/mcp-integration-plan.md` with confirmed tool names and event property names.
2. Proceed to Phase D.3 planning (feature-flagged live adapter — requires separate approval).
3. Update the demo script with a talking point about live MCP context retrieval.

### If Analytics MCP partially supports it (e.g., missing region property)

1. Document which parts work and which don't.
2. Consider using live data for what's available (e.g., funnel totals) and keeping mock for
   the Quebec/Mobile Web segmentation.
3. Be explicit in the demo: "Sandbox data confirmed checkout funnel access;
   regional segmentation depends on production event property availability."

### If Analytics MCP does not support the scenario

1. Document clearly: what tools exist, what data is available, why the scenario isn't feasible.
2. Demo stays fully mock. The architecture story remains valid and honest.
3. Update demo script: "We confirmed MCP tool access; sandbox data coverage for this specific
   segmentation scenario is TBD for production deployment."

### In all cases

- All 49 tests must continue to pass before and after any Phase D.3 work.
- Mock adapters are never removed or modified as part of live integration.
- `human_review_required = True` and `simulated_actions_only = True` remain enforced.

---

## Security Reminders

- Do not screenshot the IDE while endpoint URLs are visible in MCP config panels.
- Do not copy raw MCP responses into commit messages, PR descriptions, or chat.
- Do not share screenshots that show customer names, email addresses, or order IDs.
- If Antigravity shows a response with PII in its context panel, note the field name only.
- The `scratch/` directory is gitignored — use it for any local notes during discovery.
- Run `git status` before every commit to confirm no unexpected files are staged.
