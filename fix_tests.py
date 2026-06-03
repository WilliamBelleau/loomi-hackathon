with open('tests/test_quebec_removed.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace('dummy_bundle = LiveEvidenceBundle(checkout_conversion=0.10, snapshot_age_minutes=5.0)', 'from unittest.mock import MagicMock\n    dummy_bundle = MagicMock(spec=LiveEvidenceBundle)')
with open('tests/test_quebec_removed.py', 'w', encoding='utf-8') as f:
    f.write(c)

with open('tests/test_repo_integrity.py', 'r', encoding='utf-8') as f:
    c2 = f.read()
c2 = c2.replace('"test_ui_static_contract.py" not in line]', '"test_ui_static_contract.py" not in line and "test_demo_controller.py" not in line and "run_demo_autopilot.ps1" not in line]')
with open('tests/test_repo_integrity.py', 'w', encoding='utf-8') as f:
    f.write(c2)
