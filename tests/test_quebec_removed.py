import os
from pathlib import Path
import pytest
import json

from agent.schemas import EvidenceMode
from app.demo_controller import run_triage_for_ui, write_demo_artifact
from agent.orchestrator import Orchestrator
from tools.live_evidence_adapter import LiveEvidenceBundle

def test_no_quebec_reference_in_repo_content():
    """Scan all tracked files except this test file itself."""
    import subprocess
    result = subprocess.run(
        ["git", "grep", "-i", "quebec\\|québec"],
        capture_output=True,
        text=True
    )
    # The output might contain this file, but shouldn't contain others
    for line in result.stdout.splitlines():
        if "test_quebec_removed.py" in line:
            continue
        pytest.fail(f"Found forbidden term in repo: {line}")

def test_demo_mode_has_no_quebec_claim():
    brief = run_triage_for_ui(EvidenceMode.DEMO)
    assert "quebec" not in brief.affected_region.lower()
    assert "québec" not in brief.affected_region.lower()
    assert "quebec" not in brief.issue_title.lower()
    assert "quebec" not in brief.draft_incident_note.lower()

def test_mobile_sandbox_framing_present():
    brief = run_triage_for_ui(EvidenceMode.DEMO)
    assert "sandbox" in brief.affected_region.lower() or "sandbox" in brief.issue_title.lower()
    assert "mobile" in brief.affected_channel.lower()

def test_artifact_has_no_quebec_claim(tmp_path):
    from app import demo_controller
    brief = run_triage_for_ui(EvidenceMode.DEMO)
    
    with pytest.MonkeyPatch.context() as m:
        m.setattr(demo_controller, 'ARTIFACT_MD', tmp_path / "test.md")
        m.setattr(demo_controller, 'ARTIFACT_JSON', tmp_path / "test.json")
        m.setattr(demo_controller, 'ARTIFACTS_DIR', tmp_path)
        write_demo_artifact(brief, EvidenceMode.DEMO.value, "Demo Autopilot")
        
        content = (tmp_path / "test.json").read_text(encoding="utf-8")
        assert "quebec" not in content.lower()
        assert "québec" not in content.lower()

def test_live_bundle_path_does_not_throw_unexpected_kwarg():
    # Verify Orchestrator instantiation doesn't throw TypeError for live_bundle
    try:
        orch = Orchestrator(live_bundle=None)
    except TypeError as e:
        pytest.fail(f"Orchestrator threw TypeError for live_bundle: {e}")

def test_run_triage_for_ui_demo_does_not_require_live_bundle():
    # Uses default arguments (live_bundle omitted entirely)
    try:
        brief = run_triage_for_ui(EvidenceMode.DEMO)
        assert brief is not None
    except TypeError as e:
        pytest.fail(f"run_triage_for_ui threw TypeError: {e}")

def test_run_triage_for_ui_live_accepts_fake_bundle():
    # Pass a dummy bundle
    from unittest.mock import MagicMock
    dummy_bundle = MagicMock(spec=LiveEvidenceBundle)
    dummy_bundle.snapshot_age_minutes = 5.0
    dummy_bundle.to_analytics_signals.return_value = []
    try:
        brief = run_triage_for_ui(EvidenceMode.LIVE, live_bundle=dummy_bundle)
        assert brief is not None
    except TypeError as e:
        pytest.fail(f"run_triage_for_ui threw TypeError with live_bundle: {e}")
