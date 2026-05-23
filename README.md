# Simons Unified Commerce Signal Agent

**Bloomreach Loomi Connect AI Hackathon 2026**
**Participant:** William Belleau · La Maison Simons
**Track:** Unified Commerce Operations

---

## Project Overview

The **Simons Unified Commerce Signal Agent** is an agentic decision-support tool
that correlates behavioral analytics, customer conversation signals, and operational
error data to produce a structured triage brief for human review.

A business analyst asks:
> *"What customer experience friction should we investigate today?"*

The agent:
1. Calls the Analytics MCP adapter to detect behavioral anomalies
2. Calls the Conversations MCP adapter to identify rising friction intents
3. Calls the Synthetic Ops adapter to surface operational error signals
4. Optionally calls the Marketing MCP adapter to rule out demand-driven explanations
5. Scores the evidence transparently (additive severity + confidence)
6. Produces a structured `TriageBrief` with a draft incident note
7. Gates all output behind a visible human review requirement

**Current state:** All MCP adapters are mocked with local synthetic fixture data.
No real Bloomreach sandbox credentials are used. No external network calls are made.

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
- **Slow** — analysts must open multiple tools and join data mentally
- **Reactive** — issues are identified after customer impact accumulates
- **Expert-dependent** — signal correlation requires deep system knowledge

The agent compresses this workflow from hours to seconds, with full transparency
and a human review gate at every step.

---

## Primary Demo Scenario

**"Mobile checkout friction affecting Quebec customers."**

| Signal | Source | Value |
|---|---|---|
| Checkout-start conversion | Analytics MCP | ↓ 18% vs 7-day baseline |
| Add-to-cart rate | Analytics MCP | Stable (+0.5%) — demand not the driver |
| "payment_failed" intent | Conversations MCP | ↑ 42% |
| "cannot_complete_order" intent | Conversations MCP | ↑ 38% |
| Payment authorization failure rate | Synthetic Ops | 23% (threshold: 5%) |
| Campaign traffic spike | Marketing MCP | None detected |

**Agent output:**
- Severity: 4/5 HIGH
- Confidence: ~90%
- Suspected cause: Payment routing / authorization failure on Quebec payment path
- Recommended owner: Commerce + Payments Squad
- Draft incident note: pre-structured for human filing (not auto-filed)

---

## How to Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit UI

```bash
streamlit run app/ui_streamlit.py
```

Opens at `http://localhost:8501`.

Click **Run Triage** with the default prompt to run the demo scenario.

### 3. Run tests

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

---

## Current Mock Architecture

```
User Prompt
  → classify_prompt()
  → AnalyticsMCPClient      (loads data/analytics_anomalies.json)
  → ConversationsMCPClient  (loads data/conversation_intents.json)
  → SyntheticOpsClient      (loads data/commerce_ops_signals.json)
  → MarketingMCPClientOptional  (returns stub context)
  → EvidenceBundle
  → score_evidence()        (transparent additive scoring)
  → DeterministicReasoningEngine.build_triage_brief()
  → TriageBrief (human_review_required=True, simulated_actions_only=True)
  → Streamlit UI
```

All adapters live in `tools/`. Each has a single public method.
Scoring logic lives in `agent/scoring.py`.
Reasoning logic lives in `agent/prompts.py` behind a `ReasoningEngine` protocol.
The `agent/orchestrator.py` coordinates the pipeline.

---

## How Bloomreach MCP Integration Will Replace Mock Adapters

Each mock adapter is a single class with a single public method.
Replacing mock with real requires changing **only the method body**:

| Adapter | File | Method to replace | Phase |
|---|---|---|---|
| Analytics MCP | `tools/analytics_mcp.py` | `get_anomalies()` | Phase 2 |
| Conversations MCP | `tools/conversations_mcp.py` | `get_intent_signals()` | Phase 2 |
| Marketing MCP | `tools/marketing_mcp_optional.py` | `get_context()` | Phase 2 |
| Ops (internal) | `tools/synthetic_ops.py` | `get_ops_signals()` | Phase 3 |

The orchestrator, scoring, schema, and UI do not change.

For the reasoning step, a `GeminiReasoningEngine` can be injected via the orchestrator
constructor without touching the pipeline (see `agent/prompts.py` for integration notes).

See [`docs/mcp-usage.md`](docs/mcp-usage.md) for the full replacement guide.
See [`docs/roadmap.md`](docs/roadmap.md) for the phased plan.

---

## Responsible Design

- **Synthetic/sandbox data only** — no production Simons data, no PII
- **No secrets in repo** — `.env.example` contains only placeholder names
- **No external network calls** — all adapters are fully local
- **No automated customer-facing action** — agent recommends, humans decide
- **No real ticket creation** — draft incident note is a text artifact only
- **Human review required** — enforced by schema, UI, and tests

See [`docs/responsible-design.md`](docs/responsible-design.md) for the full statement.

---

## Judging Rubric Alignment

| Criterion | How this project addresses it |
|---|---|
| **MCP Usage** | AnalyticsMCPClient and ConversationsMCPClient are adapter-first, designed for direct Loomi Connect MCP integration. Documented swap points in every adapter. |
| **Agentic Behavior** | Full pipeline: understand → inspect → correlate → reason → recommend → prepare action. Tool trace visible in UI. |
| **Business Value** | Compresses multi-system triage from hours to seconds for commerce operations teams. |
| **Responsible AI** | human_review_required and simulated_actions_only are schema constants enforced by tests. Explainable scoring. No automated action. |
| **Demo Quality** | 5–6 minute scripted demo with pre-seeded scenario. See docs/demo-script.md. |
| **Code Quality** | Pydantic schemas, pytest suite, ReasoningEngine protocol for extensibility, clear adapter separation. |

---

## Known Gaps (Waiting on Bloomreach Sandbox Details)

- Real Bloomreach Analytics MCP endpoint, tool name, and schema
- Real Bloomreach Conversations MCP endpoint, tool name, and schema
- Real Bloomreach Marketing MCP endpoint, tool name, and schema
- LLM-based reasoning (Gemini/Vertex integration deferred to Phase 2)
- Internal Simons ops data integration (deferred to Phase 3)
- Authentication / session management for MCP calls

Until these details are available, all adapters are mocked and the demo runs
reliably from local fixture data with zero external dependencies.

---

## Project Structure

```
.
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── app/
│   ├── __init__.py
│   └── ui_streamlit.py         # Streamlit demo UI
├── agent/
│   ├── __init__.py
│   ├── orchestrator.py         # Agent pipeline
│   ├── schemas.py              # Pydantic data models
│   ├── scoring.py              # Transparent scoring
│   └── prompts.py              # ReasoningEngine protocol + DeterministicReasoningEngine
├── tools/
│   ├── __init__.py
│   ├── analytics_mcp.py        # Analytics MCP adapter (mocked)
│   ├── conversations_mcp.py    # Conversations MCP adapter (mocked)
│   ├── marketing_mcp_optional.py  # Marketing MCP adapter (mocked, optional)
│   └── synthetic_ops.py        # Synthetic ops adapter (mocked)
├── data/
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
    ├── test_scoring.py
    └── test_orchestrator.py
```
