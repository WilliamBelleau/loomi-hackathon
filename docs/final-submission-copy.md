# Final Submission Copy — Simons Unified Commerce Signal Agent
**Bloomreach Loomi Connect AI Hackathon 2026**
**Participant:** William Belleau · La Maison Simons · Team Simons Unified

---

## Project Summary (2–4 sentences)

The **Simons Unified Commerce Signal Agent** is a Python + Streamlit triage intelligence tool for Unified Commerce Business Analysts and Commerce Operations teams at omnichannel retailers. It answers one question — *"What customer experience friction should we investigate today?"* — by correlating live Bloomreach Analytics MCP signals with synthetic external commerce-ops signals into a scored, structured triage brief in seconds. The agent surfaces severity, confidence, suspected root cause, recommended owner, and a draft incident note — all gated behind a mandatory human review step with no automated action. Built for La Maison Simons, it demonstrates how Live Loomi Connect MCP intelligence compresses hours of multi-system incident triage into a single transparent artifact.

---

## MCP Usage Explanation

**Primary live integration: Bloomreach Analytics MCP via `execute_analytics_eql`**

The agent connects to Bloomreach Loomi Connect via `mcp-remote` (stdio transport) and executes sequential `execute_analytics_eql` queries to retrieve real aggregated commerce signals:

| Signal queried via MCP | Purpose |
|---|---|
| Checkout-start conversion rate vs 7-day baseline | Detect behavioral friction |
| Cart (add-to-cart) trend | Distinguish demand drop from payment failure |
| Session-to-checkout funnel drop-off | Pinpoint where customers abandon |
| Mobile funnel analysis | Isolate channel-specific friction |
| Campaign activity evidence | Rule out demand-driven spike as explanation |

The live MCP response is normalized into an internal `LiveEvidenceBundle` (Pydantic model) via `tools/live_evidence_adapter.py`, which the orchestrator consumes to generate the scored `TriageBrief`.

**Fallback strategy:** If live MCP auth or rate limits fail, a snapshot cache (`data/live_evidence_cache.json`, git-ignored) preserves demo reliability. A Demo Fixture mode uses fully synthetic data for guaranteed offline execution.

**What is intentionally synthetic:**
- Payment authorization failures, gateway routing errors, OMS/fulfillment ops signals — these don't exist in the Bloomreach sandbox and come from retailer internal systems (e.g., Datadog, Splunk).
- Customer voice / payment-failed intents — the real Conversations MCP is designed for product catalog discovery (Pacific Apparel), not checkout-friction analytics. These signals are synthetic fixtures.
- Region/geography segmentation — the sandbox dataset does not support province-level segmentation; the demo uses "All regions (sandbox dataset)" framing.

**Specific MCP tool used:** `execute_analytics_eql` (Bloomreach Loomi Connect Analytics MCP)

---

## Responsible AI Note

The Simons Unified Commerce Signal Agent is designed around four explicit guardrails:

1. **Human review required — enforced by schema and tests.**
   The `TriageBrief` schema enforces `human_review_required = True` and `simulated_actions_only = True` as constant fields. The full test suite verifies these invariants cannot be bypassed.

2. **No automated action.**
   The agent recommends next steps and produces a draft incident note, but cannot file a ticket, send a notification, or trigger any system change. All outputs are informational artifacts for human decision-making.

3. **No PII, no production data.**
   All signals are synthetic sandbox data or live-aggregated anonymized analytics from the Bloomreach sandbox. No Simons customer records, transaction data, or PII are present anywhere in the codebase, outputs, or logs.

4. **Transparent, explainable scoring.**
   Every severity and confidence point is traceable to a named signal in `agent/scoring.py`. The scoring reasoning chain is displayed in the UI and committed to the triage brief. There is no black-box inference step.

---

## What is Live vs Synthetic

| Signal | Source | Status |
|---|---|---|
| Checkout-start conversion trend | Bloomreach Analytics MCP (`execute_analytics_eql`) | ✅ Live |
| Cart (add-to-cart) trend | Bloomreach Analytics MCP (`execute_analytics_eql`) | ✅ Live |
| Session-to-checkout funnel | Bloomreach Analytics MCP (`execute_analytics_eql`) | ✅ Live |
| Mobile funnel drop-off | Bloomreach Analytics MCP (`execute_analytics_eql`) | ✅ Live |
| Campaign activity evidence | Bloomreach Analytics MCP (`execute_analytics_eql`) | ✅ Live |
| Payment authorization failure rate | Synthetic (retailer payment gateway — not in Bloomreach sandbox) | 🔶 Synthetic |
| Payment gateway routing errors | Synthetic (retailer internal ops system) | 🔶 Synthetic |
| OMS / fulfillment ops signals | Synthetic (retailer internal ops system) | 🔶 Synthetic |
| Customer "payment failed" intents | Synthetic fixture (Conversations MCP is for product catalog, not payment friction) | 🔶 Synthetic |
| Region / geography segmentation | Synthetic (sandbox dataset does not support province-level fields) | 🔶 Synthetic |
| Conversations MCP product catalog | Not used — optional stretch, wrong tool for this use case | ⬜ N/A |

---

## Demo Video Script (max 7 minutes)

### [0:00 – 0:45] Problem statement
*"Commerce operations teams lose hours correlating signals across disconnected dashboards when customers are stuck. This agent asks one question and delivers a scored, human-reviewable triage brief in seconds."*

Show the prompt: **"What customer experience friction should we investigate today?"**

Name the user: Business Analyst / Commerce Operations Lead

### [0:45 – 1:30] Architecture overview (talk over diagram)
- Live Bloomreach Analytics MCP → `execute_analytics_eql` → Agent → Scoring → TriageBrief → Human Review Gate
- Explain clearly: payment ops and customer voice are synthetic because they don't exist in the Bloomreach sandbox
- Say: *"The same pattern maps to Simons production once regional, loyalty, and store-market fields are available."*

### [1:30 – 2:00] Demo Fixture mode — fast baseline
- Select **Demo Fixture** in sidebar
- Click **Run Triage**
- Show tool trace badges (CALLED (MOCK))
- Show Severity / Confidence panel
- Say: *"This guarantees a stable narrative even offline."*

### [2:00 – 4:30] Live Loomi MCP mode — the real demo
- Switch to **Live Loomi MCP** in sidebar
- Click **Refresh Live Loomi MCP Evidence**
- Show spinner: *"Executing execute_analytics_eql against the Bloomreach sandbox..."*
- Once complete, click **Run Triage**
- Walk through:
  - Tool trace → CALLED (LIVE) badge on Analytics MCP
  - Severity 4/5 HIGH, Confidence panel
  - Evidence list — point to `[Analytics]` labels
  - Scoring breakdown
  - Draft Incident Note — *"This is not auto-filed. A human reviews and decides."*
  - Human Review Gate warning

### [4:30 – 5:30] Responsible AI callouts
- Point to `human_review_required = True` in UI
- Say: *"Enforced by schema constant and verified by the test suite — it cannot be false."*
- Say: *"simulated_actions_only = True — no ticket is created, no email is sent, no system is changed."*
- Say: *"Every severity and confidence point is traceable to a named signal. No black box."*

### [5:30 – 6:30] Judging criteria callouts
- **MCP Usage:** "We call execute_analytics_eql live against the Bloomreach Loomi Connect sandbox."
- **Agentic:** "understand → inspect → correlate → reason → recommend → prepare action — all transparent."
- **Business value:** "Hours of multi-system triage compressed to seconds."
- **Responsible AI:** "Human review gate enforced at schema level."

### [6:30 – 7:00] Wrap
*"The sandbox supports mobile funnel and campaign analytics. Payment and detailed ops signals are modeled as synthetic external commerce-system signals — exactly how a real Simons deployment would integrate. Thank you."*

---

## Final Recording Checklist

- [ ] Streamlit is running: `python -m streamlit run app/ui_streamlit.py`
- [ ] Demo Fixture mode works: Run Triage → Severity 4/5 → no TypeError
- [ ] Live MCP mode works: Refresh → Run Triage → CALLED (LIVE) badge appears
- [ ] No Quebec copy visible anywhere in UI
- [ ] Tool trace shows correct adapter labels
- [ ] Human Review Gate is visible
- [ ] Draft Incident Note section is visible
- [ ] All tests passing: `python -m pytest -v`
- [ ] Repo is public: https://github.com/WilliamBelleau/loomi-hackathon

---

## Architecture Diagram

Clean Mermaid source: `artifacts/submission_architecture_diagram.mmd`

**To export as PNG:**
1. Open https://mermaid.live
2. Paste the contents of `artifacts/submission_architecture_diagram.mmd`
3. Click **Export** → **PNG** or **SVG**
