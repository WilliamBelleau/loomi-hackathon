# Repo Audit — Simons Unified Commerce Signal Agent
## Branch: `audit-polish-v0.1`

---

## Executive Summary

**Overall verdict: Demo-ready. No critical blockers.**

49/49 tests pass. The pipeline is clean, the schema is correct, the safety invariants
(`human_review_required`, `simulated_actions_only`) are enforced by type and by tests.
The Streamlit UI tells a coherent story. The mock state is honestly labeled.

There are **no critical fixes required**. There are **7 small polish items** that would
meaningfully improve judge perception in a 5-minute demo window. None expand scope.
None touch adapters, scoring, or orchestrator logic.

---

## 1. Demo Reliability

| Check | Result | Notes |
|---|---|---|
| Judge can run from README | ✅ | Three commands, all tested |
| Install command works | ✅ | `pip install -r requirements.txt` |
| Test command works | ✅ | `python -m pytest -v` |
| Streamlit command works | ✅ | `python -m streamlit run app/ui_streamlit.py` |
| Default scenario loads without setup | ✅ | Fixtures pre-seeded, auto-loaded |
| App tells a clear story in one pass | ✅ Mostly | Minor: "Scoring reasoning" expander is easy to miss |
| Mocked MCP calls clearly labeled | ✅ | Banner + trace badges + limitations expander |
| Fresh clone would work | ⚠️ Mostly | `data/` fixtures use `Path(__file__).parent.parent` — robust, but worth a note |

**One small gap:** The README has no "Quick Start" one-liner at the very top. A judge
skimming quickly might miss the three-command setup buried under several headers.

---

## 2. Hackathon Judging Alignment

| Criterion | Score | Notes |
|---|---|---|
| **Problem relevance and clarity** | 🟢 Strong | Problem statement is specific, real, and well-framed |
| **MCP utilization and integration readiness** | 🟡 Good | Adapter pattern is excellent; swap points documented. Weakness: `docs/mcp-usage.md` is detailed but a judge browsing GitHub won't see it. The UI should say "Bloomreach Analytics MCP" not just "Analytics MCP Adapter" |
| **Agent behavior and intelligence** | 🟡 Good | Pipeline is clear. Weakness: the UI currently hides the scoring reasoning inside a collapsed expander. Judges who don't click it miss the most impressive part |
| **Execution quality and feasibility** | 🟢 Strong | Clean code, tests, schemas, no shortcuts |
| **Innovation and differentiation** | 🟡 Good | The responsible design angle is strong. Could be surfaced more prominently in the UI |

---

## 3. Streamlit UI Clarity

| UI Element | Present | Quality |
|---|---|---|
| Project purpose | ✅ | Header is clear |
| Mocked MCP state | ✅ | Banner + trace badges |
| User prompt | ✅ | Pre-filled, labeled |
| Tool trace | ✅ | Color-coded, status badges |
| Severity | ✅ | Color-coded badge |
| Confidence | ✅ | Progress bar |
| Scoring reasoning | ⚠️ | Collapsed by default — judges may miss it |
| Evidence | ✅ | Color-coded source cards |
| Suspected root cause | ✅ | Numbered list |
| Recommended owner | ✅ | Metric card |
| Recommended next steps | ✅ | Numbered list |
| Draft incident note | ✅ | Code block |
| Human review gate | ✅ | Red gate box, prominent |
| Simulated actions disclaimer | ✅ | Bottom of page |
| Agent limitations | ⚠️ | Collapsed expander — fine, but could be relabeled |

**Key UI gap:** The scoring reasoning expander label reads `"🔍 Scoring reasoning (transparent)"`.
This is the most differentiating feature of the agent and a judge has to click to see it.
Consider expanding it by default, or adding a one-line preview above the expander.

**Secondary UI gap:** The landing state (before Run Triage is clicked) is minimal.
A brief "How it works" summary or signal source legend would help judges who land cold.

---

## 4. Code Quality

### Adapter boundaries — ✅ Excellent
Each adapter is a single file, single class, single public method.
Swap points are documented in module docstrings with Phase 2 placeholder comments.

### Orchestrator readability — ✅ Excellent
The pipeline is linear, numbered, and easy to follow.
Dependency injection is clean. No hidden state.

### Schema quality — ✅ Excellent
Pydantic v2 `Literal[True]` pattern for safety invariants is correct.
All fields are documented. `EvidenceBundle` aggregation is clean.

### Scoring transparency — ✅ Excellent
Every contribution is named and logged. Additive, no black-box logic.
The marketing spike rule is correctly asymmetric (only penalizes payment hypothesis).

### Fixture path robustness — ✅ Good
`Path(__file__).parent.parent` is correct and works on fresh clone.
Minor: if someone moves a fixture file, the error message would be a raw `FileNotFoundError`
with no helpful context. Low priority.

### Import reliability — ✅
`pytest.ini` sets `pythonpath = .` — imports are resolved correctly from root.
`__init__.py` files are present in all packages.

### Test usefulness — ✅ Strong
49 tests covering:
- Scoring math (unit)
- Safety invariants (integration)
- Tool trace contents (integration)
- Demo scenario assertions (integration)
- Prompt classification (integration)

One gap: no test for `classify_prompt()` edge cases directly (covered indirectly).
Low priority for demo.

### Python version assumptions — ⚠️ Minor
`from __future__ import annotations` is used throughout — good for 3.10+.
The code uses `X | None` union syntax which requires 3.10+ at runtime with
`from __future__ import annotations`. This is fine, but README says "Python 3.11+"
and should be confirmed. Running on 3.14.0 in testing — no issues observed.

---

## 5. Responsible Design

| Commitment | Status |
|---|---|
| No production Simons data | ✅ Confirmed — fixtures only |
| No PII | ✅ Confirmed — no names, emails, order IDs |
| No secrets in repo | ✅ Confirmed — `.env.example` has placeholder names only |
| No real customer-facing action | ✅ Confirmed by design |
| No real incident/ticket creation | ✅ Confirmed — draft note is display-only |
| human_review_required always True | ✅ Enforced by `Literal[True]` + tests |
| simulated_actions_only always True | ✅ Enforced by `Literal[True]` + tests |
| No external network calls | ✅ Confirmed — no HTTP client in codebase |

**All responsible design commitments are met.**

---

## 6. Documentation Quality

| File | Quality | Gap |
|---|---|---|
| `README.md` | 🟡 Good | No quick-start one-liner at the top; opens with project name but buries setup |
| `docs/architecture.md` | ✅ Strong | Mermaid diagram is clear and accurate |
| `docs/mcp-usage.md` | ✅ Strong | Detailed, honest, well-structured |
| `docs/responsible-design.md` | ✅ Strong | Complete, explicit, well-organized |
| `docs/demo-script.md` | ✅ Strong | Timestamps, talking points, Q&A backup |
| `docs/roadmap.md` | ✅ Strong | Three-phase plan, clear gaps listed |

**Main gap:** README.md opens with the full project name and hackathon context,
but a judge scanning GitHub in 30 seconds needs to understand what the project *does*
in the first 3 lines. The current opening buries the "one question → triage brief" hook
under metadata.

---

## Critical Fixes

**None.** The project runs correctly. Tests pass. Safety invariants are enforced.

---

## Top 7 Polish Items (Ranked by Judge Impact)

> None of these add scope, new dependencies, network calls, or real integrations.
> All are pure readability and presentation improvements.

---

### P1 — README: Add a "Quick Start" block at the very top
**File:** `README.md`
**Why:** A judge who clones and opens README needs setup in 10 seconds, not after scrolling
through problem statement, demo scenario table, and architecture. Move the three commands
to a collapsible block or a clear "Quick Start" section immediately after the project title.
**Change:** Add a `## Quick Start` section with 3 commands right after the title block,
before "Project Overview".

---

### P2 — UI: Expand scoring reasoning by default (or add a preview line)
**File:** `app/ui_streamlit.py`
**Why:** The scoring reasoning is the most technically impressive and differentiating feature.
A judge watching a 5-minute demo who doesn't click the expander misses it entirely.
The demo script tells the presenter to click it, but self-navigating judges won't.
**Change:** Either set `expanded=True` on the scoring expander, or add a one-line
preview of the top reasoning item above the expander so it's always visible.

---

### P3 — UI: Improve the landing state (before Run Triage)
**File:** `app/ui_streamlit.py`
**Why:** A judge who opens the app before the demo sees a blank page with "Enter a prompt."
A simple "How this works" summary with the 4 signal sources and the demo scenario context
would orient them immediately and reinforce the MCP integration story.
**Change:** Replace the minimal landing state with a small "About this agent" card showing
the 4 adapters (Analytics MCP, Conversations MCP, Ops, Marketing MCP) and the demo scenario.

---

### P4 — UI: Add "Bloomreach Loomi Connect" to adapter names in tool trace
**File:** `app/ui_streamlit.py` (display labels) and/or `agent/orchestrator.py` (trace entry adapter names)
**Why:** The tool trace currently shows "Analytics MCP Adapter" and "Conversations MCP Adapter".
A judge seeing "Bloomreach Loomi Connect Analytics MCP" immediately connects this to the
hackathon theme. Small label change, large perception impact.
**Change:** Rename trace display labels to `"Bloomreach Analytics MCP (Loomi Connect)"` and
`"Bloomreach Conversations MCP (Loomi Connect)"`.

---

### P5 — README: Tighten the opening hook
**File:** `README.md`
**Why:** The README opens with "The Simons Unified Commerce Signal Agent is an agentic
decision-support tool that correlates behavioral analytics, customer conversation signals,
and operational error data to produce a structured triage brief for human review."
That's accurate but dense. The hook should lead with the user problem and the one-line
answer, then explain how.
**Change:** Replace the opening paragraph with a 2-sentence hook:
"Commerce operations teams waste hours correlating signals across disconnected dashboards
when customers are stuck. This agent asks one question, calls four signal adapters, and
delivers a scored, human-reviewable triage brief in seconds."

---

### P6 — Add a GitHub Actions CI workflow
**File:** `.github/workflows/ci.yml` [NEW]
**Why:** A green CI badge on the GitHub repo page signals code quality to judges browsing
the repo. It runs `python -m pytest -v` on push. One file, strong judging signal.
**Change:** Add a minimal GitHub Actions workflow that installs dependencies and runs tests
on push to `main` and on PRs.

---

### P7 — Demo script: Add a "what judges should see" checklist
**File:** `docs/demo-script.md`
**Why:** The demo script is well-structured but focuses on what the presenter says.
Adding a short "judge checklist" at the top (what the evaluator should observe during
the demo) helps if a judge reviews the repo independently without a live presentation.
**Change:** Add a brief "Evaluation checklist" section at the top of the demo script
listing the 5 key things judges should observe: tool trace, scoring transparency,
evidence correlation, human review gate, adapter-first architecture.

---

## Files Proposed to Change

| File | Change | Priority |
|---|---|---|
| `README.md` | Add Quick Start block + tighten opening hook | P1, P5 |
| `app/ui_streamlit.py` | Expand scoring reasoning + improve landing state + Bloomreach adapter labels | P2, P3, P4 |
| `agent/orchestrator.py` | Rename adapter trace labels to include "Bloomreach Loomi Connect" | P4 |
| `docs/demo-script.md` | Add judge evaluation checklist | P7 |
| `.github/workflows/ci.yml` | New — GitHub Actions CI workflow | P6 |

**Files NOT proposed to change:**
- `agent/schemas.py` — correct, no changes needed
- `agent/scoring.py` — correct, no changes needed
- `agent/prompts.py` — correct, no changes needed
- `tools/*.py` — all adapters are correct, no changes needed
- `data/*.json`, `data/*.yml` — fixtures are accurate, no changes needed
- `tests/` — all 49 tests pass, no changes needed
- `docs/architecture.md`, `docs/mcp-usage.md`, `docs/responsible-design.md`, `docs/roadmap.md` — all strong, no changes needed

---

## What Was Intentionally NOT Recommended

The following were considered and rejected as out of scope for this audit phase:
- Real Bloomreach API calls (no credentials, not in scope)
- Gemini/Vertex integration (Phase 2)
- Docker or cloud deployment (Phase 3)
- Multiple demo scenarios (scope expansion)
- Real Jira/ticketing integration (out of scope)
- Authentication framework (out of scope)
- Simons production system integrations (out of scope)

---

*Audit complete. Awaiting approval to proceed with edits.*
