# Demo Script — Simons Unified Commerce Signal Agent
# Bloomreach Loomi Connect AI Hackathon 2026
# Presenter: William Belleau, La Maison Simons
# Target duration: 5–6 minutes

---

## Pre-Demo Setup (before the clock starts)

- Open terminal in project root
- Run: `streamlit run app/ui_streamlit.py`
- Browser opens at `http://localhost:8501`
- Default prompt is pre-filled: "What customer experience friction should we investigate today?"
- Verify the mock banner is visible at the top

---

## Demo Narrative (5–6 minutes)

### 0:00 — 0:45 | Context and Problem (45 seconds)

**Say:**
> "I'm William Belleau, from La Maison Simons — a premium Canadian omnichannel retailer.
> Unified commerce teams face a constant challenge: when something goes wrong for customers,
> the signals are scattered across analytics dashboards, AI chat logs, payment systems,
> and operational monitors. Correlating these signals manually is slow, reactive, and
> requires expert knowledge that not everyone has.
>
> Today I'm showing you the Simons Unified Commerce Signal Agent — an agentic decision-support
> tool built on the Bloomreach Loomi Connect MCP framework."

**Point to:**
- Project header
- Mock banner ("All MCP calls are currently mocked — this is the honest state of the project")

---

### 0:45 — 1:15 | The Question (30 seconds)

**Say:**
> "The agent starts with a single natural language question a business analyst or
> commerce operations lead might actually ask first thing in the morning."

**Action:** Point to the pre-filled prompt:
> *"What customer experience friction should we investigate today?"*

**Say:**
> "That's it. One question. The agent does the signal correlation."

**Action:** Click **Run Triage**.

---

### 1:15 — 2:00 | Tool Trace (45 seconds)

**Say:**
> "Watch the tool trace. The agent is calling four adapters in sequence."

**Point to each trace item:**
- ✅ Analytics MCP Adapter — CALLED (MOCK) · 3 signals
- ✅ Conversations MCP Adapter — CALLED (MOCK) · 2 signals
- ✅ Synthetic Ops Adapter — CALLED (MOCK) · 1 signal
- ✅ Marketing MCP Adapter (Optional) — CALLED (MOCK) · no campaign spike

**Say:**
> "In a real deployment, the Analytics and Conversations adapters would be live
> Bloomreach Loomi Connect MCP calls. Today they're mocked with synthetic fixtures —
> and that's clearly labeled everywhere. The agent knows its own limitations."

---

### 2:00 — 2:45 | Severity, Confidence, and Scoring (45 seconds)

**Say:**
> "The agent scores the evidence transparently — no black-box ML, no magic numbers."

**Point to:**
- Severity badge (4/5 HIGH)
- Confidence bar (~90%)

**Click "Scoring reasoning" expander and read one line:**
> "Analytics: anomaly detected — 18% conversion drop vs baseline. +0.30 confidence.
> Ops: threshold-breached error signal. +1 severity, +0.25 confidence.
> Correlation: 3 independent sources. +0.15 confidence."

**Say:**
> "Every point is traceable to a named signal. A commerce operations lead can
> challenge any of these numbers."

---

### 2:45 — 3:45 | Evidence Cards and Root Causes (60 seconds)

**Scroll to evidence cards:**

**Say:**
> "Three independent signal sources are pointing at the same issue."

**Point to each card:**
- 📈 Analytics: Checkout-start conversion down 18% on Mobile Web, Quebec
- 📈 Analytics: Add-to-cart is stable — product demand is not the driver
- 💬 Conversations: 'payment_failed' intent up 42% with customer phrases like 'my payment keeps failing'
- ⚙️ Ops: Payment Gateway authorization failure rate 23% — well above the 5% threshold

**Scroll to root causes:**
> "The agent correlates these to a suspected payment routing or authorization failure
> on the Quebec payment path — not a demand issue, not a product issue."

---

### 3:45 — 4:30 | Triage Brief and Draft Incident Note (45 seconds)

**Scroll to triage brief summary:**
- Issue title, channel, region, owner recommendation: Commerce + Payments Squad

**Scroll to recommended next steps, read two:**
1. Review payment gateway authorization logs for the affected payment path
2. Prepare a customer service macro for customers experiencing checkout failures

**Scroll to draft incident note:**

**Say:**
> "The agent drafts a Jira-style incident note — pre-structured, with all the
> evidence and context. A Commerce + Payments engineer can review this, validate it,
> and file the real ticket. The agent doesn't file it."

---

### 4:30 — 5:15 | Human Review Gate and Responsible Design (45 seconds)

**Scroll to the red human review gate:**

**Say:**
> "This gate is always visible, always active. The agent is designed to produce
> a triage brief for a human — not to act autonomously.
>
> `human_review_required = True` is a constant field in the schema and enforced by tests.
> `simulated_actions_only = True` is the same. You cannot produce a brief with these false.
>
> No customer-facing action. No real ticket. No production data. No PII.
> This is responsible agentic design."

**Point to simulated actions disclaimer.**

---

### 5:15 — 5:45 | Phase 2 Path and Wrap-Up (30 seconds)

**Say:**
> "The architecture is adapter-first. Every mock adapter has a clear swap point
> documented in the code. Once Bloomreach shares sandbox credentials and tool schemas,
> we replace the method body of each adapter — the orchestrator, the scoring, and the UI
> don't change.
>
> Phase 2 also introduces a Gemini reasoning engine behind the same ReasoningEngine protocol —
> again, without touching the pipeline.
>
> The question 'What customer experience friction should we investigate today?'
> becomes a signal-correlated, scored, human-reviewed triage brief in seconds —
> not hours."

**End.**

---

## Backup / Q&A Talking Points

- **"Why not just use a dashboard?"** — Dashboards show one source at a time.
  The agent correlates across sources and surfaces the intersection.
- **"Is the scoring trustworthy?"** — Every point is traceable and displayed.
  The agent tells you why it thinks what it thinks.
- **"What about false positives?"** — Human review gate. The agent recommends,
  a human decides.
- **"What happens when MCP credentials arrive?"** — One method body replaced per adapter.
  Architecture and tests remain the same.
- **"Why Streamlit and not a full app?"** — Hackathon. Reliable demo > architecture complexity.
  Phase 3 is a proper internal tool.
