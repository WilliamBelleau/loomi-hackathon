# Demo Script – Simons Unified Commerce Signal Agent
# Bloomreach Loomi Connect AI Hackathon 2026
# Presenter: William Belleau, La Maison Simons
# Target duration: 5–6 minutes

---

## Pre-Demo Setup (before the clock starts)

- Open terminal in project root
- Run: `python -m streamlit run app/ui_streamlit.py`
- Browser opens at `http://localhost:8501`
- In the sidebar, select **Live Loomi MCP Mode** (or Snapshot Mode if network is risky).
- Default prompt is pre-filled: "What customer experience friction should we investigate today?"

---

## What Judges Should Observe

*For evaluators reviewing this repo or watching the demo – here are the key signals to look for:*

| # | What to observe | Where to see it |
|---|---|---|
| 1 | **Live MCP tool trace** | Immediately after clicking Run Triage (Analytics is LIVE, Ops is SYNTHETIC) |
| 2 | **Transparent scoring** | Scoring reasoning section (every point traced to a named signal) |
| 3 | **Evidence correlation** | Evidence cards, color-coded by source (Live vs Synthetic) |
| 4 | **Draft incident note** | Draft Incident / Jira-Style Note section |
| 5 | **Human review gate** | Red gate box at the bottom (always active, enforced by schema) |
| 6 | **Simulated actions only** | Simulated Actions disclaimer below the gate |
| 7 | **True Loomi MCP Usage** | The agent calls `mcp-remote` live and executes EQL dynamically |

---

## Demo Narrative (5–6 minutes)

### 0:00 – 0:45 | Context and Problem (45 seconds)

**Say:**
> "I'm William Belleau, from La Maison Simons – a premium Canadian omnichannel retailer.
> Unified commerce teams face a constant challenge: when something goes wrong for customers,
> the signals are scattered across analytics dashboards, AI chat logs, payment systems,
> and operational monitors. Correlating these signals manually is slow, reactive, and
> requires expert knowledge that not everyone has.
>
> Today I'm showing you the Simons Unified Commerce Signal Agent – an agentic decision-support
> tool built directly onto the Bloomreach Loomi Connect MCP framework."

---

### 0:45 – 1:15 | The Question (30 seconds)

**Say:**
> "The agent starts with a single natural language question a business analyst or
> commerce operations lead might actually ask first thing in the morning."

**Action:** Point to the pre-filled prompt:
> *"What customer experience friction should we investigate today?"*

**Say:**
> "That's it. One question. The agent does the signal correlation."

**Action:** Click **Run Triage**.

---

### 1:15 – 2:00 | Tool Trace (45 seconds)

**Say:**
> "Watch the tool trace. The agent is pulling real context from Bloomreach."

**Point to the trace items:**
- 📈 Analytics MCP Adapter – CALLED (LIVE)
- 💬 Conversations MCP Adapter – CALLED (SYNTHETIC)
- ⚙️ Synthetic Ops Adapter – CALLED (SYNTHETIC)

**Say:**
> "The Analytics adapter is connecting live to Loomi Connect via `mcp-remote` and executing EQL to pull real checkout drop-off data. 
> To complete the omnichannel triage scenario, the Ops and Conversations data are synthetic fixtures—representing internal retailer systems like Datadog or OMS that don't exist in the Bloomreach sandbox."

---

### 2:00 – 2:45 | Severity, Confidence, and Scoring (45 seconds)

**Say:**
> "The agent scores the evidence transparently – no black-box ML, no magic numbers."

**Point to:**
- Severity badge (4/5 HIGH)
- Confidence bar (~90%)

**Click "Scoring reasoning" expander and read one line:**
> "Analytics: anomaly detected – 18% conversion drop vs baseline. +0.30 confidence.
> Ops: threshold-breached error signal. +1 severity, +0.25 confidence.
> Correlation: 3 independent sources. +0.15 confidence."

**Say:**
> "Every point is traceable to a named signal. A commerce operations lead can
> challenge any of these numbers."

---

### 2:45 – 3:45 | Evidence Cards and Root Causes (60 seconds)

**Scroll to evidence cards:**

**Say:**
> "Live Bloomreach signals and synthetic Ops signals are pointing at the exact same issue."

**Point to each card:**
- 📉 Analytics (Live): Checkout-start conversion down on Mobile Web
- 📉 Analytics (Live): Add-to-cart is stable – product demand is not the driver
- 💬 Conversations (Synthetic): 'payment_failed' intent up 42%
- ⚙️ Ops (Synthetic): Payment Gateway authorization failure rate 23%

**Scroll to root causes:**
> "The agent correlates these to a suspected payment routing or authorization failure
> on the payment path – not a demand issue, not a product issue."

---

### 3:45 – 4:30 | Triage Brief and Draft Incident Note (45 seconds)

**Scroll to triage brief summary:**
- Issue title, channel, region, owner recommendation: Commerce + Payments Squad

**Scroll to recommended next steps, read two:**
1. Review payment gateway authorization logs for the affected payment path
2. Prepare a customer service macro for customers experiencing checkout failures

**Scroll to draft incident note:**

**Say:**
> "The agent drafts a Jira-style incident note – pre-structured, with all the
> evidence and context. A Commerce + Payments engineer can review this, validate it,
> and file the real ticket. The agent doesn't file it."

---

### 4:30 – 5:15 | Human Review Gate and Responsible Design (45 seconds)

**Scroll to the red human review gate:**

**Say:**
> "This gate is always visible, always active. The agent is designed to produce
> a triage brief for a human – not to act autonomously.
>
> `human_review_required = True` is a constant field in the schema and enforced by tests.
> `simulated_actions_only = True` is the same. You cannot produce a brief with these false.
>
> No customer-facing action. No real ticket. No production data. No PII.
> This is responsible agentic design."

**Point to simulated actions disclaimer.**

---

### 5:15 – 5:45 | Extensibility and Wrap-Up (30 seconds)

**Say:**
> "The architecture is modular. We already replaced the mock Analytics adapter with a live Loomi Connect MCP client. For a retailer to take this to production, they would just plug their internal Datadog API into the Ops adapter.
>
> The question 'What customer experience friction should we investigate today?'
> becomes a signal-correlated, scored, human-reviewed triage brief in seconds –
> not hours."

**End.**

---

## Backup / Q&A Talking Points

- **"Why not just use a dashboard?"** – Dashboards show one source at a time.
  The agent correlates across sources and surfaces the intersection.
- **"Is the scoring trustworthy?"** – Every point is traceable and displayed.
  The agent tells you why it thinks what it thinks.
- **"What about false positives?"** – Human review gate. The agent recommends,
  a human decides.
- **"Why are some adapters synthetic?"** – The live Loomi Connect integration handles the Analytics and Marketing context. The synthetic adapters represent proprietary retailer systems (OMS, payment gateways) that naturally wouldn't exist inside a Bloomreach demo sandbox.
- **"What about the LLM integration?"** – The triage brief assembly runs via a `ReasoningEngine` protocol. It currently uses a deterministic implementation for demo reliability, but swapping to an LLM like Gemini is as simple as injecting a new class.
- **"Why Streamlit and not a full app?"** — Hackathon. Reliable demo > architecture complexity. Phase 3 is a proper internal tool.


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
