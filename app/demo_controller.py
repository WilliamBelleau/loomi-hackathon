import os
import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from agent.schemas import EvidenceMode, TriageBrief
from agent.orchestrator import Orchestrator
from tools.live_mcp_client import refresh_live_mcp_evidence, LiveEvidenceBundle
from tools.live_evidence_adapter import LiveEvidenceAdapter

ARTIFACTS_DIR = Path("artifacts")
ARTIFACT_MD = ARTIFACTS_DIR / "demo_autopilot_latest.md"
ARTIFACT_JSON = ARTIFACTS_DIR / "demo_autopilot_latest.json"

def _sanitize_string(text: str) -> str:
    """Removes any potentially sensitive information like endpoint URLs or project IDs."""
    if not text:
        return text
    # Mask common endpoint URLs
    text = text.replace("loomi-mcp-alpha.bloomreach.com", "<REDACTED_ENDPOINT>")
    # Mask project IDs and tokens if any happen to leak into the brief strings
    # The triage brief shouldn't contain these natively, but just to be safe.
    env_url = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL", "")
    if env_url and env_url in text:
        text = text.replace(env_url, "<REDACTED_ENDPOINT>")
    env_id = os.environ.get("LOOMI_MCP_PROJECT_ID", "")
    if env_id and env_id in text:
        text = text.replace(env_id, "<REDACTED_PROJECT_ID>")
    
    return text

def _sanitize_dict(d: dict) -> dict:
    sanitized = {}
    for k, v in d.items():
        if isinstance(v, str):
            sanitized[k] = _sanitize_string(v)
        elif isinstance(v, list):
            sanitized[k] = [_sanitize_string(i) if isinstance(i, str) else i for i in v]
        elif isinstance(v, dict):
            sanitized[k] = _sanitize_dict(v)
        else:
            sanitized[k] = v
    return sanitized

def refresh_live_evidence_for_ui(progress_callback=None) -> LiveEvidenceBundle:
    """
    Refreshes live evidence by calling the live MCP client.
    """
    def _noop(msg): pass
    cb = progress_callback or _noop
    return asyncio.run(refresh_live_mcp_evidence(cb))

def load_last_successful_refresh_for_ui() -> Optional[LiveEvidenceBundle]:
    """
    Loads the last successful MCP refresh from cache.
    """
    adapter = LiveEvidenceAdapter()
    return adapter.load_snapshot()

def run_triage_for_ui(mode: EvidenceMode, live_bundle: Optional[LiveEvidenceBundle] = None, prompt: str = "What customer experience friction should we investigate today?") -> TriageBrief:
    """
    Runs the agent orchestration to generate a TriageBrief.
    """
    orchestrator = Orchestrator(
        evidence_mode=mode,
        live_bundle=live_bundle
    )
    return orchestrator.run(prompt)

def write_demo_artifact(brief: TriageBrief, mode: str, source: str) -> None:
    """
    Writes sanitized MD and JSON artifacts of the triage output.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Prepare JSON
    raw_dict = brief.model_dump()
    sanitized_dict = _sanitize_dict(raw_dict)
    
    metadata = {
        "timestamp": timestamp,
        "mode": mode,
        "source": source
    }
    
    output_json = {
        "_meta": metadata,
        "brief": sanitized_dict
    }
    
    with open(ARTIFACT_JSON, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2)
        
    # Prepare Markdown
    md_lines = []
    md_lines.append("# Demo Autopilot: Triage Brief Artifact")
    md_lines.append(f"**Timestamp**: {timestamp}")
    md_lines.append(f"**Mode**: {mode}")
    md_lines.append(f"**Source**: {source}")
    md_lines.append("")
    md_lines.append("## Responsible Design Notes")
    md_lines.append("- **human_review_required**: `True` (Enforced by schema)")
    md_lines.append("- **simulated_actions_only**: `True` (Enforced by schema)")
    md_lines.append("- Data is sanitized. No raw MCP responses or PII.")
    md_lines.append("")
    
    md_lines.append("## Triage Output")
    md_lines.append(f"**Issue Title**: {_sanitize_string(brief.issue_title)}")
    md_lines.append(f"**Severity**: {brief.severity}/5")
    md_lines.append(f"**Confidence**: {brief.confidence:.0%}")
    md_lines.append("")
    
    md_lines.append("### Tool Trace")
    for trace in brief.tool_trace:
        md_lines.append(f"- {trace.adapter} (Status: {trace.status.value}, Signals: {trace.signal_count})")
    md_lines.append("")
    
    md_lines.append("### Top Evidence")
    for ev in brief.evidence:
        md_lines.append(f"- {_sanitize_string(ev)}")
    md_lines.append("")
    
    md_lines.append("### Draft Incident Note")
    md_lines.append("```")
    md_lines.append(_sanitize_string(brief.draft_incident_note))
    md_lines.append("```")
    
    with open(ARTIFACT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
