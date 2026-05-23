"""
ui_streamlit.py — Streamlit UI for the Simons Unified Commerce Signal Agent.

Demo narrative layout (single page, top to bottom):
  1. Project header + hackathon badge
  2. Mock data banner
  3. Prompt input + Run Triage button
  4. Tool trace (adapter calls)
  5. Severity + Confidence
  6. Triage brief summary
  7. Evidence cards
  8. Suspected root causes
  9. Recommended next steps
  10. Draft incident / Jira-style note
  11. Human review gate
  12. Simulated actions only disclaimer
"""
import streamlit as st

from agent.orchestrator import Orchestrator

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Simons Unified Commerce Signal Agent",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f4c75 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid #334155;
    }

    .mock-banner {
        background: linear-gradient(90deg, #78350f, #92400e);
        color: #fde68a;
        padding: 0.75rem 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1.5rem;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .severity-badge {
        display: inline-block;
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.05em;
    }

    .evidence-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.6rem;
        font-size: 0.875rem;
        color: #e2e8f0;
    }

    .evidence-card.analytics { border-left: 4px solid #3b82f6; }
    .evidence-card.conversations { border-left: 4px solid #8b5cf6; }
    .evidence-card.ops { border-left: 4px solid #ef4444; }
    .evidence-card.marketing { border-left: 4px solid #10b981; }

    .trace-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0.9rem;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 6px;
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: #94a3b8;
    }

    .trace-badge {
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        background: #1e3a5f;
        color: #60a5fa;
        white-space: nowrap;
    }

    .trace-badge.skipped {
        background: #1a1a2e;
        color: #64748b;
    }

    .human-review-gate {
        background: linear-gradient(135deg, #450a0a, #7f1d1d);
        border: 2px solid #dc2626;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        text-align: center;
    }

    .sim-disclaimer {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-top: 1rem;
        font-size: 0.8rem;
        color: #a8a29e;
    }

    .section-label {
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="main-header">
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:0.5rem;">
            <span style="font-size:2.2rem;">🛍️</span>
            <div>
                <div style="font-size:1.6rem; font-weight:700; color:#f8fafc; line-height:1.2;">
                    Simons Unified Commerce Signal Agent
                </div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.25rem;">
                    La Maison Simons · Bloomreach Loomi Connect AI Hackathon 2026
                </div>
            </div>
        </div>
        <div style="font-size:0.875rem; color:#cbd5e1; margin-top:0.75rem; max-width:700px;">
            Agentic triage for unified commerce operations.
            Correlates analytics anomalies, customer conversation signals, and operational errors
            to produce a structured brief for human review.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Mock data banner
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="mock-banner">
        ⚠️ <strong>MOCK MODE ACTIVE:</strong>
        All MCP adapter calls are currently served from local synthetic fixture data.
        Analytics MCP, Conversations MCP, and Marketing MCP are not yet connected to
        Bloomreach sandbox endpoints. No real data. No network calls.
        This will be replaced once Bloomreach sandbox credentials are available.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Input + Run button
# ---------------------------------------------------------------------------

DEFAULT_PROMPT = "What customer experience friction should we investigate today?"

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_prompt = st.text_area(
        "Triage prompt",
        value=DEFAULT_PROMPT,
        height=68,
        label_visibility="collapsed",
        key="triage_prompt",
        placeholder="e.g. What customer experience friction should we investigate today?",
    )

with col_btn:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    run_clicked = st.button(
        "🔍 Run Triage",
        type="primary",
        use_container_width=True,
        key="run_triage_btn",
    )

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------

if run_clicked:
    with st.spinner("Running triage pipeline…"):
        orchestrator = Orchestrator()
        try:
            brief = orchestrator.run(user_prompt)
        except ValueError as exc:
            st.error(f"❌ {exc}")
            st.stop()

    st.markdown("---")

    # -----------------------------------------------------------------------
    # Tool trace
    # -----------------------------------------------------------------------

    st.markdown('<div class="section-label">🔧 Tool Trace — Adapter Calls</div>', unsafe_allow_html=True)

    for entry in brief.tool_trace:
        is_skipped = entry.status.value == "SKIPPED"
        badge_class = "skipped" if is_skipped else ""
        icon = "⏭️" if is_skipped else "✅"
        count_str = f" · {entry.signal_count} signal(s)" if not is_skipped else ""
        st.markdown(
            f"""
            <div class="trace-item">
                <span>{icon}</span>
                <span style="flex:1; color:#e2e8f0; font-weight:500;">{entry.adapter}</span>
                <span class="trace-badge {badge_class}">{entry.status.value}</span>
                <span style="color:#64748b; font-size:0.8rem;">{count_str} {entry.note}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------------------------
    # Severity + Confidence
    # -----------------------------------------------------------------------

    st.markdown('<div class="section-label">📊 Severity &amp; Confidence</div>', unsafe_allow_html=True)

    severity_colors = {
        1: ("#065f46", "#34d399"),  # green
        2: ("#064e3b", "#6ee7b7"),
        3: ("#78350f", "#fbbf24"),  # amber
        4: ("#7c2d12", "#fb923c"),  # orange
        5: ("#7f1d1d", "#f87171"),  # red
    }
    severity_labels = {1: "LOW", 2: "LOW-MED", 3: "MEDIUM", 4: "HIGH", 5: "CRITICAL"}

    bg, fg = severity_colors.get(brief.severity, ("#1e293b", "#e2e8f0"))
    sev_label = severity_labels.get(brief.severity, str(brief.severity))

    col_sev, col_conf, col_blank = st.columns([1, 2, 3])
    with col_sev:
        st.markdown(
            f"""
            <div style="background:{bg}; border:1px solid {fg}; border-radius:10px;
                        padding:1rem; text-align:center;">
                <div style="font-size:0.75rem; color:{fg}; font-weight:600;
                            letter-spacing:0.08em; margin-bottom:0.3rem;">SEVERITY</div>
                <div style="font-size:2.2rem; font-weight:800; color:{fg};">
                    {brief.severity}/5
                </div>
                <div style="font-size:0.8rem; color:{fg}; font-weight:600;">
                    {sev_label}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_conf:
        st.markdown(
            f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:10px;
                        padding:1rem;">
                <div style="font-size:0.75rem; color:#94a3b8; font-weight:600;
                            letter-spacing:0.08em; margin-bottom:0.5rem;">CONFIDENCE</div>
                <div style="font-size:1.8rem; font-weight:700; color:#e2e8f0;">
                    {brief.confidence:.0%}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.progress(brief.confidence, text=f"Signal confidence: {brief.confidence:.0%}")

    with st.expander("🔍 Scoring reasoning (transparent)"):
        st.markdown(brief.reasoning_summary)

    # -----------------------------------------------------------------------
    # Triage brief summary
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.markdown('<div class="section-label">📋 Triage Brief</div>', unsafe_allow_html=True)
    st.markdown(f"### {brief.issue_title}")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Affected Journey", brief.affected_journey)
        st.metric("Channel", brief.affected_channel)
    with col_b:
        st.metric("Region", brief.affected_region)
        st.metric("Recommended Owner", brief.owner_recommendation)
    with col_c:
        st.markdown("**Customer Impact**")
        st.caption(brief.customer_impact)

    st.markdown("**Business Impact**")
    st.info(brief.business_impact)

    # -----------------------------------------------------------------------
    # Evidence cards
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.markdown('<div class="section-label">🔬 Evidence</div>', unsafe_allow_html=True)

    for item in brief.evidence:
        if item.startswith("[Analytics]"):
            card_class = "analytics"
            icon = "📈"
        elif item.startswith("[Conversations]"):
            card_class = "conversations"
            icon = "💬"
        elif item.startswith("[Ops]"):
            card_class = "ops"
            icon = "⚙️"
        elif item.startswith("[Marketing]"):
            card_class = "marketing"
            icon = "📣"
        else:
            card_class = ""
            icon = "•"

        st.markdown(
            f'<div class="evidence-card {card_class}">{icon} {item}</div>',
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------------------------
    # Suspected root causes
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.markdown('<div class="section-label">🔎 Suspected Root Causes</div>', unsafe_allow_html=True)
    for i, cause in enumerate(brief.suspected_root_causes, 1):
        st.markdown(f"**{i}.** {cause}")

    # -----------------------------------------------------------------------
    # Recommended next steps
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.markdown('<div class="section-label">✅ Recommended Next Steps</div>', unsafe_allow_html=True)
    for i, step in enumerate(brief.recommended_next_steps, 1):
        st.markdown(f"{i}. {step}")

    # -----------------------------------------------------------------------
    # Draft incident note
    # -----------------------------------------------------------------------

    st.markdown("---")
    st.markdown('<div class="section-label">📝 Draft Incident / Jira-Style Note</div>', unsafe_allow_html=True)
    st.code(brief.draft_incident_note, language="text")

    # -----------------------------------------------------------------------
    # Human review gate
    # -----------------------------------------------------------------------

    st.markdown(
        """
        <div class="human-review-gate">
            <div style="font-size:1.8rem; margin-bottom:0.5rem;">🚦</div>
            <div style="font-size:1.1rem; font-weight:700; color:#fca5a5; margin-bottom:0.5rem;">
                HUMAN REVIEW REQUIRED
            </div>
            <div style="font-size:0.875rem; color:#fecaca; max-width:500px; margin:0 auto;">
                No action may be taken based on this triage brief without explicit human review
                and approval. This agent does not create tickets, send messages, or execute
                any business action autonomously.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Simulated actions disclaimer
    # -----------------------------------------------------------------------

    st.markdown(
        """
        <div class="sim-disclaimer">
            🔒 <strong>Simulated Actions Only.</strong>
            All outputs from this agent are informational and for human review only.
            No real Jira tickets, incidents, customer communications, payment interventions,
            or operational changes are created or executed by this system.
            Current MCP adapters are mocked with synthetic fixture data.
            Production Simons data and PII are never used.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Agent limitations
    with st.expander("ℹ️ Agent limitations & known gaps"):
        for lim in brief.limitations:
            st.markdown(f"- {lim}")

else:
    # Landing state
    st.markdown(
        """
        <div style="text-align:center; padding:3rem 0; color:#475569;">
            <div style="font-size:3rem; margin-bottom:1rem;">🔍</div>
            <div style="font-size:1.1rem; font-weight:500;">
                Enter a triage prompt above and click <strong>Run Triage</strong> to begin.
            </div>
            <div style="font-size:0.875rem; margin-top:0.5rem; color:#64748b;">
                Default scenario: Mobile checkout friction affecting Quebec customers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
