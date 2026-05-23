# Roadmap — Simons Unified Commerce Signal Agent

## Phase 1 — Mock-First Hackathon Frame (Current)

**Status: Complete**

Goal: Demonstrate end-to-end agentic triage behavior with synthetic data and
clearly labeled mock adapters. Show the full pipeline: understand → inspect →
correlate → reason → recommend → prepare action.

### Delivered
- [x] Pydantic schemas for all signal types and triage output
- [x] AnalyticsMCPClient (mocked, fixture-backed)
- [x] ConversationsMCPClient (mocked, fixture-backed)
- [x] SyntheticOpsClient (mocked, fixture-backed)
- [x] MarketingMCPClientOptional (mocked, stub)
- [x] Transparent additive scoring (severity + confidence)
- [x] ReasoningEngine protocol + DeterministicReasoningEngine
- [x] Orchestrator pipeline with tool trace
- [x] Streamlit UI with demo narrative layout
- [x] human_review_required = True (constant, tested)
- [x] simulated_actions_only = True (constant, tested)
- [x] pytest suite (scoring + orchestrator)
- [x] Architecture, MCP usage, responsible design, and demo docs

### Known Gaps (waiting on external details)
- Real Bloomreach Analytics MCP endpoint, tool name, and schema
- Real Bloomreach Conversations MCP endpoint, tool name, and schema
- Real Bloomreach Marketing MCP endpoint, tool name, and schema
- LLM-based reasoning (no Gemini/Vertex dependency yet)
- Internal Simons ops data source (payment gateway, OMS)

---

## Phase 2 — Bloomreach Sandbox MCP Integration

**Status: Planned — blocked on Bloomreach sandbox access**

Goal: Replace all Bloomreach mock adapters with real Loomi Connect MCP calls.
Introduce LLM-based reasoning. Validate signal quality on sandbox data.

### Planned Work

#### 2.1 — Analytics MCP Integration
- Obtain sandbox credentials and endpoint from Bloomreach
- Identify exact tool name and request/response schema
- Replace `AnalyticsMCPClient.get_anomalies()` body with authenticated MCP call
- Validate that sandbox signals match fixture data structure
- Update `AnalyticsSignal` schema if Bloomreach schema differs

#### 2.2 — Conversations MCP Integration
- Same pattern as Analytics
- Replace `ConversationsMCPClient.get_intent_signals()` body
- Validate intent naming conventions against Loomi's taxonomy

#### 2.3 — Marketing MCP Integration (Optional)
- Replace `MarketingMCPClientOptional.get_context()` body
- Validate campaign traffic spike detection logic

#### 2.4 — Gemini Reasoning Engine
- Implement `GeminiReasoningEngine` behind the `ReasoningEngine` protocol
- Build structured prompt from `EvidenceBundle` + `ScoringResult`
- Parse JSON-structured response into `TriageBrief`
- Inject via orchestrator constructor — no orchestrator code changes
- Add `google-generativeai` to `requirements.txt`
- Add `GEMINI_API_KEY` to `.env.example`

#### 2.5 — Expanded Test Coverage
- Add integration tests against sandbox endpoints
- Add prompt regression tests (LLM output stability)
- Add latency tests (triage must complete < 10 seconds)

---

## Phase 3 — Production Hardening for Unified Commerce Operations

**Status: Future — requires Phase 2 completion**

Goal: Evolve from a hackathon demo to a reliable internal tool for Simons
unified commerce operations.

### Planned Work

#### 3.1 — Internal Ops Data Integration
- Connect `SyntheticOpsClient` to real payment gateway observability (Datadog, Splunk, or equivalent)
- Connect to OMS event stream for inventory and fulfillment signals
- Define `OpsSignal` schema alignment with internal data formats

#### 3.2 — Multi-Scenario Support
- Support multiple concurrent triage scenarios (not just checkout)
- Add scenario templates: inventory discrepancy, fulfillment delay, search relevance

#### 3.3 — Operational Tooling
- Add structured logging and audit trail for all triage runs
- Store `TriageBrief` history for trend analysis
- Add triage run comparison (before/after incident resolution)

#### 3.4 — UI Enhancements
- Replace Streamlit with internal tool (React or Next.js)
- Add authentication (SSO / Simons IAM)
- Add triage history view and run comparison

#### 3.5 — Human Review Workflow Integration
- Add a "Submit for Review" action that opens a pre-filled Jira/ServiceNow form
- The form is populated from `draft_incident_note` — no auto-submission
- Human clicks "Submit" in the ticketing system

#### 3.6 — Monitoring and Quality
- Add feedback loop: triage analysts rate brief quality
- Track false positive / false negative rate over time
- Refine scoring thresholds based on operational feedback

---

## Guiding Principles Across All Phases

- **Adapter-first**: Each data source has a dedicated adapter. New sources = new adapter.
  Core pipeline does not change.
- **Human review at every stage**: `human_review_required = True` is permanent.
  Automation assists, humans decide.
- **Transparent scoring**: Every severity/confidence point remains explainable.
  No black-box inference without explanation.
- **No production data in demos**: All demo and test runs use synthetic or sandbox data.
- **Incremental, validated**: Each phase produces a tested, runnable system before
  the next phase begins.
