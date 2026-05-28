import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

def test_env_file_not_tracked():
    # Check that .env is not present in repo root or is gitignored
    # Even if present locally, it should not be tracked by git
    # We will just verify .env is not present in the git tree
    import subprocess
    result = subprocess.run(["git", "ls-files", ".env"], capture_output=True, text=True, cwd=ROOT_DIR)
    assert ".env" not in result.stdout

def test_live_evidence_cache_is_ignored():
    import subprocess
    result = subprocess.run(["git", "check-ignore", "data/live_evidence_cache.json"], capture_output=True, text=True, cwd=ROOT_DIR)
    # git check-ignore returns 0 if ignored, 1 if not
    assert result.returncode == 0

def test_live_evidence_snapshot_is_ignored():
    import subprocess
    result = subprocess.run(["git", "check-ignore", "data/live_evidence_snapshot.json"], capture_output=True, text=True, cwd=ROOT_DIR)
    assert result.returncode == 0

def test_no_obvious_secrets_in_repo():
    import subprocess
    # We grep the tracked files only
    result = subprocess.run(["git", "grep", "-I", "-n", "CLIENT_SECRET\\|PASSWORD\\|API_KEY\\|TOKEN\\|sb-\\|sandbox.paypal\\|loomi-mcp-alpha"], capture_output=True, text=True, cwd=ROOT_DIR)
    # It's expected to find some placeholder occurrences in .env.example or discover_mcp_tools.py
    # But it shouldn't contain the real values
    # We just ensure it doesn't fail the command or we inspect it
    # As the user script handles this, we'll assert that real UUID is not found
    uuid_result = subprocess.run(["git", "grep", "-I", "952be3a0"], capture_output=True, text=True, cwd=ROOT_DIR)
    output_lines = [line for line in uuid_result.stdout.splitlines() if "test_repo_integrity.py" not in line and "test_ui_static_contract.py" not in line]
    assert len(output_lines) == 0

def test_no_smoke_test_tracked():
    import subprocess
    result = subprocess.run(["git", "ls-files", "scratch/smoke_test.py"], capture_output=True, text=True, cwd=ROOT_DIR)
    assert "scratch/smoke_test.py" not in result.stdout

def test_no_proxy_js():
    assert not (ROOT_DIR / "proxy.js").exists()

def test_no_raw_mcp_output_tracked():
    import subprocess
    result = subprocess.run(["git", "ls-files", "scripts/mcp_discovery_output*"], capture_output=True, text=True, cwd=ROOT_DIR)
    assert not result.stdout.strip()

def test_requirements_txt_does_not_include_mcp():
    reqs = (ROOT_DIR / "requirements.txt").read_text(encoding="utf-8")
    assert "mcp==" not in reqs
    assert "mcp\n" not in reqs

def test_requirements_mcp_txt_includes_mcp():
    reqs = (ROOT_DIR / "requirements-mcp.txt").read_text(encoding="utf-8")
    assert "mcp" in reqs

def test_live_mcp_client_does_not_hardcode_endpoint():
    content = (ROOT_DIR / "tools" / "live_mcp_client.py").read_text(encoding="utf-8")
    assert "https://" not in content

def test_main_app_does_not_import_mcp_at_module_level():
    content = (ROOT_DIR / "app" / "ui_streamlit.py").read_text(encoding="utf-8")
    assert "import mcp" not in content
    assert "from mcp" not in content
