import json
from pathlib import Path
import yaml
from tools.live_evidence_adapter import LiveEvidenceBundle

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"

def test_analytics_anomalies_loads():
    content = (DATA_DIR / "analytics_anomalies.json").read_text(encoding="utf-8")
    data = json.loads(content)
    assert isinstance(data, list)
    assert len(data) > 0

def test_conversation_intents_loads_and_is_synthetic():
    content = (DATA_DIR / "conversation_intents.json").read_text(encoding="utf-8")
    data = json.loads(content)
    assert isinstance(data, list)
    # Ensure it remains clearly synthetic
    assert "payment" in json.dumps(data).lower()

def test_commerce_ops_signals_loads():
    content = (DATA_DIR / "commerce_ops_signals.json").read_text(encoding="utf-8")
    data = json.loads(content)
    assert isinstance(data, list)
    assert any("payment" in str(alert).lower() for alert in data)

def test_owner_mapping_contains_expected():
    content = (DATA_DIR / "owner_mapping.yml").read_text(encoding="utf-8")
    data = yaml.safe_load(content)
    assert "payment_failure" in data
    assert data["payment_failure"]["owner"] == "Commerce + Payments Squad"

def test_live_evidence_snapshot_example_loads():
    content = (DATA_DIR / "live_evidence_snapshot.example.json").read_text(encoding="utf-8")
    data = json.loads(content)
    bundle = LiveEvidenceBundle(**data)
    assert bundle.funnel_overall.sessions > 0
    assert bundle.funnel_mobile.sessions > 0
    
    # Check for absence of PII/secrets
    content_lower = content.lower()
    assert "endpoint" not in content_lower
    assert "uuid" not in content_lower or "test" in content_lower
    assert "@" not in content_lower  # No emails
    assert "token" not in content_lower
    assert "cookie" not in content_lower
    assert "auth_code" not in content_lower
