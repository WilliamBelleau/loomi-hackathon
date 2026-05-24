"""
ui_streamlit.py — Streamlit UI for the Simons Unified Commerce Signal Agent.

Brand design: Simons-inspired editorial retail aesthetic.
  Light intake zone  : white/linen background, ink text, forest-green accents.
  Dark results zone  : analytical dark panels for evidence/triage output.
  Typography         : system-safe Inter / Georgia stacks — no remote fonts.
  Rendering          : st.html() for all custom HTML (Streamlit 1.45+).
                       st.markdown() for Markdown-only content.
"""

import streamlit as st

from agent.orchestrator import Orchestrator

# ─── Page config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Simons Unified Commerce Signal Agent",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Global CSS — injected once via st.html so it is guaranteed rendered ─────

st.html("""
<style>
/* ── Design tokens ──────────────────────────────────────────────────────── */
:root {
    --ink:        #1d1d1b;
    --charcoal:   #1C1C1E;
    --green:      #007853;
    --deep-green: #2D6A4F;
    --white:      #FFFFFF;
    --linen:      #f7f5f0;
    --stone:      #e8e4dc;
    --muted:      #6f6b64;
    --border:     #dedbd3;
    --dark-bg:    #0f172a;
    --dark-panel: #1e293b;
    --dark-border:#334155;
    --font-body:    'Inter', 'Helvetica Neue', Arial, sans-serif;
    --font-heading: 'Cormorant Garamond', Georgia, 'Times New Roman', serif;
}

/* ── Page background ────────────────────────────────────────────────────── */
html, body, .stApp,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"],
[data-testid="stVerticalBlock"] {
    background-color: var(--linen) !important;
    font-family: var(--font-body) !important;
    color: var(--ink) !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* ── Default text ─────────────────────────────────────────────────── */
/* Intentionally not using broad color:inherit to avoid cascade pollution */

/* ── Headings inside st.markdown ─────────────────────────────────────────── */
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li { color: var(--ink) !important; }

/* ── HR dividers ─────────────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Button → charcoal / green hover ──────────────────────────────────────── */
.stButton > button,
.stButton > button[kind="primary"],
.stButton > button[kind="secondary"],
[data-testid="stBaseButton-primary"],
[data-testid="stBaseButton-secondary"] {
    background: #1C1C1E !important;
    background-color: #1C1C1E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.65rem 1rem !important;
    transition: background .18s !important;
    width: 100% !important;
    cursor: pointer !important;
}
.stButton > button p,
[data-testid="stBaseButton-primary"] p,
[data-testid="stBaseButton-secondary"] p {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}
.stButton > button:hover,
[data-testid="stBaseButton-primary"]:hover {
    background: #007853 !important;
    background-color: #007853 !important;
}
.stButton > button:focus-visible,
[data-testid="stBaseButton-primary"]:focus-visible {
    outline: 2px solid #007853 !important;
    outline-offset: 3px !important;
}
/* Hide sidebar and its toggle arrow completely */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

/* ── Textarea ────────────────────────────────────────────────────────────── */
.stTextArea textarea {
    background: var(--white) !important;
    color: var(--ink) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 2px !important;
    font-family: var(--font-body) !important;
    font-size: 0.95rem !important;
    caret-color: var(--green) !important;
}
.stTextArea textarea:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(0,120,83,.13) !important;
}
.stTextArea label { display: none !important; }

/* ── Metric ──────────────────────────────────────────────────────────────── */
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: .75rem !important; letter-spacing: .07em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: var(--ink) !important; }

/* ── Progress bar ────────────────────────────────────────────────────────── */
.stProgress > div > div { background: var(--green) !important; }
[data-testid="stProgressBarText"] { color: var(--muted) !important; font-size: .8rem !important; }

/* ── Info / alert ────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: #f0faf5 !important;
    border-left-color: var(--green) !important;
    color: var(--ink) !important;
    border-radius: 2px !important;
}
[data-testid="stAlertContentInfo"] { color: var(--ink) !important; }

/* ── Code block ──────────────────────────────────────────────────────────── */
[data-testid="stCode"], .stCode {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
}
code { color: var(--ink) !important; font-size: .82rem !important; }

/* ── Expander ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p { color: var(--ink) !important; font-weight: 600 !important; }
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p { color: var(--ink) !important; }

/* ── Caption ─────────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] { color: var(--muted) !important; font-size: .82rem !important; }

/* ── Spinner ─────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] * { color: var(--green) !important; }
</style>
""")

# ─── Header ───────────────────────────────────────────────────────────────────

st.html("""
<div style="
    background: #FFFFFF;
    border-bottom: 2.5px solid #007853;
    padding: 1.75rem 0 1.4rem 0;
    margin-bottom: 1.1rem;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
">
  <div style="display:flex; align-items:center; gap:0.85rem; margin-bottom:0.5rem;">
    <div style="
        width:34px; height:38px; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        color:#007853; font-size:1.6rem; line-height:1;
    ">&#127807;</div>
    <div>
      <div style="
          font-size: 0.69rem;
          font-weight: 700;
          letter-spacing: 0.22em;
          text-transform: uppercase;
          color: #6f6b64;
          margin-bottom: 0.3rem;
          font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
      ">La Maison Simons &nbsp;·&nbsp; Bloomreach Loomi Connect AI Hackathon 2026</div>
      <div style="
          font-family: 'Cormorant Garamond', Georgia, 'Times New Roman', serif;
          font-size: 2rem;
          font-weight: 400;
          letter-spacing: 0.01em;
          color: #1d1d1b;
          line-height: 1.15;
      ">Unified Commerce Signal Agent</div>
    </div>
  </div>
  <div style="
      font-size: 0.88rem;
      color: #6f6b64;
      line-height: 1.55;
      max-width: 580px;
      font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
      margin-top: 0.2rem;
  ">
    Correlates analytics anomalies, customer conversation signals, and operational
    errors into a scored, human-reviewable triage brief &mdash; in seconds.
  </div>
</div>
""")

# ─── Mock-mode banner ─────────────────────────────────────────────────────────

st.html("""
<div style="
    background: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 2px;
    padding: 0.65rem 1rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin-bottom: 1.1rem;
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
">
  &#9888;&nbsp; <strong>MOCK MODE</strong> &mdash; All Bloomreach MCP adapter calls use local
  synthetic fixtures. Not connected to Bloomreach sandbox. No network calls.
  No production data. No PII.
</div>
""")

# ─── Prompt input + Run Triage ────────────────────────────────────────────────

DEFAULT_PROMPT = "What customer experience friction should we investigate today?"

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_prompt = st.text_area(
        "triage_prompt_label",
        value=DEFAULT_PROMPT,
        height=70,
        label_visibility="collapsed",
        key="triage_prompt",
        placeholder="e.g. What customer experience friction should we investigate today?",
    )
with col_btn:
    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    run_clicked = st.button(
        "Run Triage →",
        type="primary",
        use_container_width=True,
        key="run_triage_btn",
    )

# ─── Agent pipeline ───────────────────────────────────────────────────────────

if run_clicked:
    with st.spinner("Running triage pipeline…"):
        orchestrator = Orchestrator()
        try:
            brief = orchestrator.run(user_prompt)
        except ValueError as exc:
            st.error(f"❌ {exc}")
            st.stop()

    # ── Divider: light intake → dark results ─────────────────────────────────
    st.html("""
    <div style="
        height: 3px;
        background: linear-gradient(90deg, #007853, #2D6A4F);
        margin: 1.5rem 0 1.25rem 0;
    "></div>
    """)

    # ── Tool trace ────────────────────────────────────────────────────────────
    _TRACE_DISPLAY_LABELS = {
        "Analytics MCP Adapter":            "Bloomreach Loomi Connect — Analytics MCP",
        "Conversations MCP Adapter":        "Bloomreach Loomi Connect — Conversations MCP",
        "Synthetic Ops Adapter":            "Synthetic Commerce Ops Adapter",
        "Marketing MCP Adapter (Optional)": "Optional Bloomreach Marketing MCP Context",
    }

    trace_rows = ""
    for entry in brief.tool_trace:
        display_name = _TRACE_DISPLAY_LABELS.get(entry.adapter, entry.adapter)
        is_skipped   = entry.status.value == "SKIPPED"
        icon         = "⏭" if is_skipped else "✅"
        badge_bg     = "#1a1a2e" if is_skipped else "#1e3a5f"
        badge_fg     = "#64748b" if is_skipped else "#60a5fa"
        count_str    = f" · {entry.signal_count} signal(s)" if not is_skipped else ""
        trace_rows += f"""
        <div style="
            display:flex; align-items:center; gap:0.7rem;
            padding:0.52rem 0.85rem;
            background:#0f172a; border:1px solid #1e293b; border-radius:3px;
            margin-bottom:0.35rem;
            font-size:0.82rem; color:#94a3b8;
            font-family:'Inter','Helvetica Neue',Arial,sans-serif;
        ">
          <span>{icon}</span>
          <span style="flex:1; color:#e2e8f0; font-weight:500;">{display_name}</span>
          <span style="
              font-size:0.63rem; font-weight:700; padding:0.15rem 0.45rem;
              border-radius:2px; background:{badge_bg}; color:{badge_fg};
              white-space:nowrap; letter-spacing:0.06em;
          ">{entry.status.value}</span>
          <span style="color:#64748b; font-size:0.76rem;">{count_str} {entry.note}</span>
        </div>"""

    st.html(f"""
    <div style="font-family:'Inter','Helvetica Neue',Arial,sans-serif; margin-bottom:0.5rem;">
      <div style="
          font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
          text-transform:uppercase; color:#64748b;
          padding-bottom:0.35rem; border-bottom:1px solid #1e293b;
          margin-bottom:0.6rem;
      ">🔧 Tool Trace — Adapter Calls</div>
      {trace_rows}
    </div>
    """)

    # ── Severity + Confidence ─────────────────────────────────────────────────
    severity_colors = {
        1: ("#065f46", "#34d399"),
        2: ("#064e3b", "#6ee7b7"),
        3: ("#78350f", "#fbbf24"),
        4: ("#7c2d12", "#fb923c"),
        5: ("#7f1d1d", "#f87171"),
    }
    severity_labels = {1: "LOW", 2: "LOW-MED", 3: "MEDIUM", 4: "HIGH", 5: "CRITICAL"}
    bg, fg = severity_colors.get(brief.severity, ("#1e293b", "#e2e8f0"))
    sev_label = severity_labels.get(brief.severity, str(brief.severity))

    st.html(f"""
    <div style="font-family:'Inter','Helvetica Neue',Arial,sans-serif; margin-bottom:0.5rem;">
      <div style="
          font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
          text-transform:uppercase; color:#64748b;
          padding-bottom:0.35rem; border-bottom:1px solid #1e293b;
          margin-bottom:0.75rem;
      ">📊 Severity &amp; Confidence</div>
      <div style="display:flex; gap:1rem; align-items:stretch;">
        <div style="
            background:{bg}; border:1px solid {fg}; border-radius:3px;
            padding:1rem 1.25rem; text-align:center; min-width:110px;
        ">
          <div style="font-size:0.63rem; color:{fg}; font-weight:700;
                      letter-spacing:0.14em; text-transform:uppercase;
                      margin-bottom:0.25rem;">Severity</div>
          <div style="font-size:2.1rem; font-weight:800; color:{fg}; line-height:1.1;">
              {brief.severity}/5</div>
          <div style="font-size:0.72rem; color:{fg}; font-weight:700;
                      letter-spacing:0.1em; margin-top:0.15rem;">{sev_label}</div>
        </div>
        <div style="
            background:#1e293b; border:1px solid #334155; border-radius:3px;
            padding:1rem 1.25rem; min-width:140px;
        ">
          <div style="font-size:0.63rem; color:#94a3b8; font-weight:700;
                      letter-spacing:0.14em; text-transform:uppercase;
                      margin-bottom:0.25rem;">Confidence</div>
          <div style="font-size:2.1rem; font-weight:800; color:#e2e8f0; line-height:1.1;">
              {brief.confidence:.0%}</div>
          <div style="font-size:0.72rem; color:#94a3b8; margin-top:0.15rem;">
              {int(brief.confidence * 100)} / 100 signal confidence score</div>
        </div>
      </div>
    </div>
    """)

    st.progress(brief.confidence, text=f"Signal confidence: {brief.confidence:.0%}")
    with st.expander("🔍 Scoring reasoning (transparent)", expanded=True):
        st.markdown(brief.reasoning_summary)

    # ── Triage brief ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.html("""<div style="
        font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
        text-transform:uppercase; color:#6f6b64;
        padding-bottom:0.4rem; border-bottom:1px solid #dedbd3;
        margin-bottom:0.75rem;
        font-family:'Inter','Helvetica Neue',Arial,sans-serif;
    ">📋 Triage Brief</div>""")
    # Issue title — using st.html to avoid Streamlit blue link coloring on headings
    issue_escaped = brief.issue_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    st.html(f"""
    <div style="
        font-family: 'Cormorant Garamond', Georgia, serif;
        font-size: 1.55rem;
        font-weight: 600;
        color: #1d1d1b;
        line-height: 1.25;
        margin: 0.5rem 0 1rem 0;
        letter-spacing: 0.01em;
    ">{issue_escaped}</div>
    """)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Affected Journey", brief.affected_journey)
        st.metric("Channel", brief.affected_channel)
    with col_b:
        st.metric("Region", brief.affected_region)
        st.metric("Recommended Owner", brief.owner_recommendation)
    with col_c:
        cust_impact_escaped = brief.customer_impact.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        st.html(f"""
        <div style="
            font-size:0.75rem; font-weight:600; letter-spacing:0.08em;
            text-transform:uppercase; color:#6f6b64;
            margin-bottom:0.4rem; font-family:'Inter','Helvetica Neue',Arial,sans-serif;
        ">Customer Impact</div>
        <div style="
            font-size:0.84rem; color:#1d1d1b; line-height:1.5;
            font-family:'Inter','Helvetica Neue',Arial,sans-serif;
        ">{cust_impact_escaped}</div>
        """)

    biz_impact_escaped = brief.business_impact.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    st.html(f"""
    <div style="
        background: #f0faf5;
        border: 1px solid #a7f3d0;
        border-left: 4px solid #007853;
        border-radius: 3px;
        padding: 0.75rem 1rem;
        font-size: 0.87rem;
        color: #1d1d1b;
        line-height: 1.55;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
        margin-top: 0.5rem;
    ">{biz_impact_escaped}</div>
    """)

    # ── Evidence cards ────────────────────────────────────────────────────────
    st.markdown("---")
    st.html("""<div style="
        font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
        text-transform:uppercase; color:#64748b;
        padding-bottom:0.35rem; border-bottom:1px solid #1e293b;
        margin-bottom:0.65rem;
        font-family:'Inter','Helvetica Neue',Arial,sans-serif;
    ">🔬 Evidence</div>""")

    for item in brief.evidence:
        if item.startswith("[Analytics]"):
            accent, icon = "#3b82f6", "📈"
        elif item.startswith("[Conversations]"):
            accent, icon = "#8b5cf6", "💬"
        elif item.startswith("[Ops]"):
            accent, icon = "#ef4444", "⚙"
        elif item.startswith("[Marketing]"):
            accent, icon = "#10b981", "📣"
        else:
            accent, icon = "#475569", "·"
        st.html(f"""
        <div style="
            background:#1e293b; border:1px solid #334155;
            border-left:4px solid {accent};
            border-radius:3px; padding:0.8rem 1rem; margin-bottom:0.4rem;
            font-size:0.84rem; color:#e2e8f0; line-height:1.45;
            font-family:'Inter','Helvetica Neue',Arial,sans-serif;
        ">{icon}&nbsp; {item}</div>
        """)

    # ── Suspected root causes ─────────────────────────────────────────────────
    st.markdown("---")
    st.html("""<div style="
        font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
        text-transform:uppercase; color:#6f6b64;
        padding-bottom:0.4rem; border-bottom:1px solid #dedbd3;
        margin-bottom:0.65rem;
        font-family:'Inter','Helvetica Neue',Arial,sans-serif;
    ">🔎 Suspected Root Causes</div>""")
    causes_html = ""
    for i, cause in enumerate(brief.suspected_root_causes, 1):
        c = cause.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        causes_html += f"""
        <div style="
            display:flex; gap:0.6rem; align-items:baseline;
            margin-bottom:0.55rem;
            font-family:'Inter','Helvetica Neue',Arial,sans-serif;
            font-size:0.88rem; color:#1d1d1b; line-height:1.5;
        ">
          <span style="flex-shrink:0; font-weight:700; color:#1d1d1b;">{i}.</span>
          <span style="color:#1d1d1b;">{c}</span>
        </div>"""
    st.html(f"<div spellcheck='false'>{causes_html}</div>")

    # ── Recommended next steps ────────────────────────────────────────────────
    st.markdown("---")
    st.html("""<div style="
        font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
        text-transform:uppercase; color:#6f6b64;
        padding-bottom:0.4rem; border-bottom:1px solid #dedbd3;
        margin-bottom:0.65rem;
        font-family:'Inter','Helvetica Neue',Arial,sans-serif;
    ">✅ Recommended Next Steps</div>""")
    steps_html = ""
    for i, step in enumerate(brief.recommended_next_steps, 1):
        s = step.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        steps_html += f"""
        <div style="
            display:flex; gap:0.6rem; align-items:baseline;
            margin-bottom:0.5rem;
            font-family:'Inter','Helvetica Neue',Arial,sans-serif;
            font-size:0.88rem; color:#1d1d1b; line-height:1.5;
        ">
          <span style="flex-shrink:0; min-width:1.2rem; font-weight:700; color:#007853;">{i}.</span>
          <span style="color:#1d1d1b;">{s}</span>
        </div>"""
    st.html(f"<div spellcheck='false'>{steps_html}</div>")

    # ── Draft incident note ───────────────────────────────────────────────────
    st.markdown("---")
    st.html("""<div style="
        font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
        text-transform:uppercase; color:#6f6b64;
        padding-bottom:0.4rem; border-bottom:1px solid #dedbd3;
        margin-bottom:0.65rem;
        font-family:'Inter','Helvetica Neue',Arial,sans-serif;
    ">📝 Draft Incident / Jira-Style Note</div>""")
    note_escaped = (brief.draft_incident_note
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;'))
    st.html(f"""
    <pre style="
        background: #1e293b;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 1.25rem 1.4rem;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 0.81rem;
        line-height: 1.65;
        overflow-x: auto;
        white-space: pre-wrap;
        word-break: break-word;
        margin: 0;
    ">{note_escaped}</pre>
    """)

    # ── Human review gate ─────────────────────────────────────────────────────
    st.html("""
    <div style="
        background: linear-gradient(135deg, #450a0a, #7f1d1d);
        border: 2px solid #dc2626;
        border-radius: 4px;
        padding: 1.4rem 1.25rem;
        margin-top: 1.25rem;
        text-align: center;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    ">
      <div style="font-size:1.5rem; margin-bottom:0.35rem;">🚦</div>
      <div style="
          font-size:0.9rem; font-weight:700; color:#fca5a5;
          letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.4rem;
      ">Human Review Required</div>
      <div style="font-size:0.83rem; color:#fecaca; max-width:460px; margin:0 auto; line-height:1.55;">
        No action may be taken without explicit human review and approval.
        This agent does not create tickets, send messages, or execute
        any business action autonomously.
      </div>
    </div>
    """)

    # ── Simulated actions disclaimer ──────────────────────────────────────────
    st.html("""
    <div style="
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 3px;
        padding: 0.85rem 1.1rem;
        margin-top: 0.6rem;
        font-size: 0.77rem;
        color: #a8a29e;
        line-height: 1.5;
        font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    ">
      &#128274; <strong>Simulated Actions Only.</strong> All outputs are informational and for
      human review only. No real Jira tickets, incidents, customer communications, or operational
      changes are created by this system. Current MCP adapters are mocked with synthetic fixture
      data. Production Simons data and PII are never used.
    </div>
    """)

    with st.expander("ℹ️ Agent limitations & known gaps"):
        for lim in brief.limitations:
            st.markdown(f"- {lim}")

else:
    # ── Landing state — adapter card grid ────────────────────────────────────
    st.html("""
    <div style="font-family:'Inter','Helvetica Neue',Arial,sans-serif; margin-top:0.5rem;">
      <div style="
          font-size:0.63rem; font-weight:700; letter-spacing:0.2em;
          text-transform:uppercase; color:#6f6b64;
          padding-bottom:0.4rem; border-bottom:1px solid #dedbd3;
          margin-bottom:0.9rem;
      ">Signal Adapters</div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.85rem; margin-bottom:1rem;">

        <div style="background:#fff; border:1px solid #dedbd3; border-left:4px solid #3b82f6; border-radius:2px; padding:0.9rem 1.1rem;">
          <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#6f6b64; margin-bottom:0.2rem;">Bloomreach Loomi Connect</div>
          <div style="font-size:0.9rem; font-weight:600; color:#1d1d1b; margin-bottom:0.25rem;">Analytics MCP</div>
          <div style="font-size:0.78rem; color:#6f6b64; line-height:1.45; margin-bottom:0.55rem;">Conversion anomaly detection &middot; funnel signal inspection &middot; trend analysis</div>
          <span style="display:inline-block; font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; background:#FEF3C7; color:#92400E; padding:0.12rem 0.5rem; border-radius:2px;">&#9888; Mocked Today</span>
        </div>

        <div style="background:#fff; border:1px solid #dedbd3; border-left:4px solid #8b5cf6; border-radius:2px; padding:0.9rem 1.1rem;">
          <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#6f6b64; margin-bottom:0.2rem;">Bloomreach Loomi Connect</div>
          <div style="font-size:0.9rem; font-weight:600; color:#1d1d1b; margin-bottom:0.25rem;">Conversations MCP</div>
          <div style="font-size:0.78rem; color:#6f6b64; line-height:1.45; margin-bottom:0.55rem;">Customer friction intent trends &middot; representative phrase extraction</div>
          <span style="display:inline-block; font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; background:#FEF3C7; color:#92400E; padding:0.12rem 0.5rem; border-radius:2px;">&#9888; Mocked Today</span>
        </div>

        <div style="background:#fff; border:1px solid #dedbd3; border-left:4px solid #ef4444; border-radius:2px; padding:0.9rem 1.1rem;">
          <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#6f6b64; margin-bottom:0.2rem;">Synthetic Commerce Ops</div>
          <div style="font-size:0.9rem; font-weight:600; color:#1d1d1b; margin-bottom:0.25rem;">Payment + OMS Signals</div>
          <div style="font-size:0.78rem; color:#6f6b64; line-height:1.45; margin-bottom:0.55rem;">Authorization failure rates &middot; fulfillment delay signals &middot; threshold alerts</div>
          <span style="display:inline-block; font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; background:#FEF3C7; color:#92400E; padding:0.12rem 0.5rem; border-radius:2px;">&#9888; Mocked Today</span>
        </div>

        <div style="background:#fff; border:1px solid #dedbd3; border-left:4px solid #007853; border-radius:2px; padding:0.9rem 1.1rem;">
          <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:#6f6b64; margin-bottom:0.2rem;">Optional &middot; Bloomreach Marketing MCP</div>
          <div style="font-size:0.9rem; font-weight:600; color:#1d1d1b; margin-bottom:0.25rem;">Campaign Context</div>
          <div style="font-size:0.78rem; color:#6f6b64; line-height:1.45; margin-bottom:0.55rem;">Traffic spike detection &middot; rules out demand-driven anomaly explanations</div>
          <span style="display:inline-block; font-size:0.62rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; background:#FEF3C7; color:#92400E; padding:0.12rem 0.5rem; border-radius:2px;">&#9888; Mocked Today</span>
        </div>

      </div>

      <div style="font-size:0.8rem; color:#6f6b64; border-top:1px solid #dedbd3; padding-top:0.85rem; line-height:1.55;">
        &#127919; <strong style="color:#1d1d1b;">Demo scenario:</strong>
        Mobile checkout friction affecting Quebec customers &mdash;
        checkout-start conversion &darr;18%&nbsp;&middot;&nbsp;
        payment_failed intents &uarr;42%&nbsp;&middot;&nbsp;
        authorization failure rate above threshold.
        <br><br>
        &#11014; Enter the triage prompt above and click
        <strong style="color:#1d1d1b;">Run Triage &rarr;</strong>
        to execute the full agent pipeline.
      </div>
    </div>
    """)
