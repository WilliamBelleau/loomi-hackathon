# Simons Unified Commerce Signal Agent

**Bloomreach Loomi Connect AI Hackathon 2026**
**Participant:** William Belleau · La Maison Simons
**Track:** Unified Commerce Operations

---

## ⚡ Quick Start

```powershell
pip install -r requirements.txt                      # install dependencies
python -m pytest -v                                  # run 49 tests (all should pass)
python -m streamlit run app/ui_streamlit.py          # launch demo → http://localhost:8501
```

Click **Run Triage** with the default prompt. No setup, no credentials, no network calls required.

---

## Project Overview

Commerce operations teams lose hours correlating signals across disconnected dashboards
when customers are stuck. This agent asks one question and delivers a scored,
human-reviewable triage brief in seconds — without requiring expert knowledge.

> *"What customer experience friction should we investigate today?"*

The agent:
1. Calls the Analytics MCP adapter to detect behavioral anomalies
2. Calls the Conversations MCP adapter to identify rising friction intents
3. Calls the Synthetic Ops adapter to surface operational error signals
4. Optionally calls the Marketing MCP adapter to rule out demand-driven explanations
5. Scores the evidence transparently (additive severity + confidence)
6. Produces a structured `TriageBrief` with a draft incident note
7. Gates all output behind a visible human review requirement

**Current state:** This is a true Live Loomi MCP demo.
- Streamlit can call Loomi Connect MCP through `mcp-remote`
- Uses `execute_analytics_eql` to pull aggregated checkout/cart/funnel/campaign signals
- Normalizes the response directly into the triage agent
- **Cache is fallback only**: protects demo reliability if auth/rate limits fail (Last Successful MCP Refresh is not the primary live path)
- **Synthetic ops is intentional**: payment authorization failures, gateway routing, OMS/fulfillment context do not exist in the Bloomreach sandbox and would come from retailer commerce systems.
- **Conversations MCP is an optional stretch**: actual Conversations MCP is designed for product discovery / catalog search, not used for payment-friction analytics.

---

## What is Live vs Synthetic

### Live
* checkout trend
* cart trend
* session-to-checkout funnel
* mobile funnel
* campaign activity check

### Synthetic
* payment authorization failure
* payment gateway path
* OMS/fulfillment ops signal
* checkout step failure
* region/province segmentation

### Optional/stretch
* Conversations MCP product discovery catalog

---

## Target User

- Unified Commerce Business Analyst
- Senior Commerce Product Owner
- IT Incident Triage Lead / Commerce Operations Manager

---

## Problem Statement

Unified commerce teams at omnichannel retailers investigate customer-impacting issues
across disconnected systems: analytics dashboards, AI chat logs, payment gateways,
OMS, and fulfillment monitors.

Manually correlating these signals is:
- **Slow** – analysts must open multiple tools and join data mentally
- **Reactive** – issues are identified after customer impact accumulates
- **Expert-dependent** – signal correlation requires deep system knowledge

The agent compresses this workflow from hours to seconds, with full transparency
and a human review gate at every step.

---

## Primary Demo Scenario

**"Mobile checkout friction affecting customers (sandbox demo dataset)."**

| Signal | Source | Value |
|---|---|---|
| Checkout-start conversion | Analytics MCP | ↓ 18% vs 7-day baseline |
| Add-to-cart rate | Analytics MCP | Stable (+0.5%) – demand not the driver |
| "payment_failed" intent | Conversations MCP | ↑ 42% |
| "cannot_complete_order" intent | Conversations MCP | ↑ 38% |
| Payment authorization failure rate | Synthetic Ops | 23% (threshold: 5%) |
| Campaign traffic spike | Marketing MCP | None detected |

**Agent output:**
- Severity: 4/5 HIGH
- Confidence: ~90%
- Suspected cause: Payment routing / authorization failure on payment path
- Recommended owner: Commerce + Payments Squad
- Draft incident note: pre-structured for human filing (not auto-filed)

---

## How to Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-mcp.txt
```

### 2. Run the Streamlit UI

```powershell
python -m streamlit run app/ui_streamlit.py
```

Opens at `http://localhost:8501`.

Click **Run Triage** with the default prompt to run the demo scenario.

### Execution Modes

The agent supports the following execution modes directly from the UI sidebar:
- **Demo Fixture Mode**: Uses local deterministic mock files (`data/*.json`). Guarantees the mobile checkout friction narrative.
- **Live Loomi MCP Mode**: Connects live to `execute_analytics_eql` over `mcp-remote` to pull real funnel metrics. If unavailable, falls back gracefully.
- **Last Successful Refresh (Snapshot Mode)**: Reads `data/live_evidence_snapshot.json` created by previous live MCP runs. Protects demo reliability against rate limits.

### 3. Run tests

```powershell
python -m pytest -v
```

*(Optional)* Run Live E2E test with explicit env vars:
```bash
LOOMI_MCP_ANALYTICS_MARKETING_URL=https://... LOOMI_MCP_PROJECT_ID=... RUN_LIVE_MCP_E2E=1 python -m pytest -v tests/integration/test_live_mcp_e2e.py
```

---

## Judge-Facing Architecture Summary

**Live Analytics MCP → Agent Reasoning → Synthetic External Ops Context → Human Review Gate**

```
User Prompt
  ↓ classify_prompt()
  ↓ AnalyticsMCPClient      (Live execute_analytics_eql or Cache Fallback)
  ↓ MarketingMCPClient      (Live campaign check or Cache Fallback)
  ↓ ConversationsMCPClient  (Synthetic customer voice fixture)
  ↓ SyntheticOpsClient      (Synthetic internal ops/payment fixture)
  ↓ EvidenceBundle
  ↓ score_evidence()        (transparent additive scoring)
  ↓ DeterministicReasoningEngine.build_triage_brief()
  ↓ TriageBrief (human_review_required=True, simulated_actions_only=True)
  ↓ Streamlit UI
```

---

## Responsible Design

- **Synthetic/sandbox data only** — no production Simons data, no PII
- **No secrets in repo** — `.env.example` contains only placeholder names
- **Limited external network** — connects only to Bloomreach Sandbox, no internal Simons systems
- **No automated customer-facing action** — agent recommends, humans decide
- **No real ticket creation** — draft incident note is a text artifact only
- **Human review required** — enforced by schema, UI, and tests

See [`docs/responsible-design.md`](docs/responsible-design.md) for the full statement.

---

## Judging Rubric Alignment

| Criterion | How this project addresses it |
|---|---|
| **MCP Usage** | Connects live to `execute_analytics_eql` over Loomi Connect via `mcp-remote`. |
| **Agentic Behavior** | Full pipeline: understand → inspect → correlate → reason → recommend → prepare action. Tool trace visible in UI. |
| **Business Value** | Compresses multi-system triage from hours to seconds for commerce operations teams. |
| **Responsible AI** | human_review_required and simulated_actions_only are schema constants enforced by tests. Explainable scoring. No automated action. |
| **Demo Quality** | 5–6 minute scripted demo with pre-seeded scenario. See docs/demo-script.md. |
| **Code Quality** | Pydantic schemas, pytest suite, ReasoningEngine protocol for extensibility, clear adapter separation. |

---


## Project Structure

```
.
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-mcp.txt
├── pytest.ini
├── app/
│   ├── __init__.py
│   └── ui_streamlit.py         # Streamlit demo UI
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py         # Agent pipeline
│   ├── schemas.py              # Pydantic data models
│   ├── scoring.py              # Transparent scoring
│   └── prompts.py              # ReasoningEngine protocol
├── tools/
│   ├── __init__.py
│   ├── live_mcp_client.py      # Live execute_analytics_eql runner
│   ├── live_evidence_adapter.py # Live bundle normalization
│   ├── analytics_mcp.py        # Analytics MCP adapter (mock fallback)
│   ├── conversations_mcp.py    # Conversations MCP adapter (mock fallback)
│   ├── marketing_mcp_optional.py # Marketing MCP adapter (mock fallback)
│   └── synthetic_ops.py        # Synthetic ops adapter (fixture)
├── data/
│   ├── live_evidence_snapshot.json # Generated snapshot
│   ├── analytics_anomalies.json
│   ├── conversation_intents.json
│   ├── commerce_ops_signals.json
│   └── owner_mapping.yml
├── docs/
│   ├── architecture.md
│   ├── mcp-usage.md
│   ├── responsible-design.md
│   ├── demo-script.md
│   └── roadmap.md
└── tests/
    ├── integration/
    │   └── test_live_mcp_e2e.py
    ├── test_scoring.py
    ├── test_orchestrator.py
    └── ... (Comprehensive tests for schema, repo integrity, UI, and live components)
```
