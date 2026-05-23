# Responsible Design — Simons Unified Commerce Signal Agent

## Principles

This project is built on the principle that AI agents in commerce operations
must be transparent, bounded, and human-supervised. The following commitments
apply to all versions of this system.

---

## Data

### ✅ Synthetic / Sandbox Data Only
All data used in this project is synthetically generated for demo purposes.
No real Simons transaction data, customer data, or operational data is used at any stage.

### ✅ No Production Simons Data
This system does not connect to any Simons production database, analytics platform,
ERP, OMS, or payment system. All signal data is loaded from local JSON/YAML fixture files.

### ✅ No Personally Identifiable Information (PII)
No customer names, email addresses, phone numbers, order IDs, payment card data,
or any other PII is present in any fixture file, output, log, or configuration.
This is an invariant — not a best-effort commitment.

---

## Credentials and Secrets

### ✅ No Secrets in the Repository
No API keys, tokens, passwords, or credentials of any kind are committed to this repository.
The `.env.example` file contains only placeholder variable names with no values.
The `.gitignore` file excludes `.env` files from version control.

### ✅ No External Network Calls
The current implementation makes no outbound network requests.
All adapter calls are resolved locally from fixture files.

---

## Agent Actions

### ✅ No Automated Customer-Facing Actions
This agent does not send emails, push notifications, chat messages, or any
communication to customers. All outputs are internal, informational, and for
human review only.

### ✅ No Real Ticket or Incident Creation
The draft incident note produced by this agent is a text artifact displayed
in the Streamlit UI. It is not filed to Jira, ServiceNow, PagerDuty, or any
incident management system. No integrations with ticketing systems exist.

### ✅ All Business-Impacting Actions Are Simulated
The agent can recommend actions (e.g., investigate payment routing, prepare a
customer service macro). It cannot execute any of these actions. All
recommended actions require human decision and manual execution.

### ✅ Human Review Required Before Any Action
The `TriageBrief` schema enforces `human_review_required = True` as a constant field.
The Streamlit UI displays a prominent human review gate on every triage output.
Tests enforce this invariant — a brief with `human_review_required = False` cannot be produced.

---

## Transparency

### ✅ Explainable Scoring
The severity and confidence scores are computed by a transparent, additive function
(`agent/scoring.py`). Every point of severity or confidence is traceable to a named signal.
The scoring reasoning is displayed in the UI and included in the `TriageBrief`.

### ✅ Tool Trace
Every adapter call is logged with its status (MOCK / LIVE / SKIPPED) and included
in the triage brief output. Users and reviewers can see exactly which data sources
contributed to the brief.

### ✅ Mock State Clearly Labeled
The Streamlit UI displays a prominent banner indicating that all MCP calls are
currently mocked with synthetic fixture data. The tool trace labels each adapter
as MOCK. The `limitations` field of the `TriageBrief` enumerates all current gaps.

---

## Summary Table

| Commitment | Status |
|---|---|
| Synthetic/sandbox data only | ✅ Enforced |
| No production Simons data | ✅ Enforced |
| No PII | ✅ Enforced |
| No secrets in repo | ✅ Enforced via .gitignore |
| No external network calls | ✅ Enforced (no HTTP clients in codebase) |
| No customer-facing automation | ✅ Enforced by design |
| No real ticket/incident creation | ✅ No ticketing integrations |
| All actions simulated | ✅ simulated_actions_only = True (constant) |
| Human review required | ✅ human_review_required = True (constant, tested) |
| Transparent scoring | ✅ Additive, explainable, displayed in UI |
