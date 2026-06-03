import os
import re

replacements = [
    (r'customers (sandbox demo dataset)', r'customers (sandbox demo dataset)'),
    (r'payment path', r'payment path'),
    (r'Guarantees the mobile checkout friction narrative.', r'Guarantees the mobile checkout friction narrative.'),
    (r'sandbox routing', r'sandbox routing'),
    (r'Mobile Checkout Friction — Sandbox Dataset —', r'Mobile Checkout Friction — Sandbox Dataset —'),
    (r'Customers on Mobile Web are unable', r'Customers on Mobile Web are unable'),
    (r'\'Quebec\', \'Ontario\', \'All\'', r'\'All regions (sandbox dataset)\''),
    (r'Mobile checkout friction affecting customers (sandbox demo dataset) &mdash;', r'Demo scenario: mobile checkout friction in the sandbox commerce journey &mdash;'),
    (r'"region": "All regions / sandbox dataset"', r'"region": "All regions / sandbox dataset"'),
    (r'conversion is within', r'conversion is within'),
    (r'the "Mobile Web checkout drop" scenario', r'the "Mobile Web checkout drop" scenario'),
    (r'\(e\.g\., Quebec, Ontario\)', r'(e.g., US, Canada)'),
    (r'region/country', r'region/country'),
    (r'"mobile checkout friction affecting customers (sandbox demo dataset)"\?', r'"mobile checkout friction"?'),
    (r'or customers (sandbox demo dataset)\?', r'or specific region customers?'),
    (r'the Mobile Web segmentation', r'the Mobile Web segmentation'),
    (r'on the payment path', r'on the payment path'),
    (r'affected_region="All regions / sandbox dataset"', r'affected_region="All regions / sandbox dataset"'),
    (r'assert "All regions / sandbox dataset" not in brief.affected_region', r'assert "All regions / sandbox dataset" not in brief.affected_region'),
    (r'test_affected_region_is_sandbox', r'test_affected_region_is_sandbox'),
    (r'assert brief.affected_region == "All regions / sandbox dataset"', r'assert brief.affected_region == "All regions / sandbox dataset"'),
    (r'assert brief.affected_region != "All regions / sandbox dataset"', r'assert brief.affected_region != "All regions / sandbox dataset"'),
    (r'assert "All regions / sandbox dataset" in brief.affected_region', r'assert "All regions / sandbox dataset" in brief.affected_region'),
    (r'test_default_demo_mode_returns_sandbox_demo', r'test_default_demo_mode_returns_sandbox_demo'),
    (r'region="All regions / sandbox dataset"', r'region="All regions / sandbox dataset"'),
    (r'in the Mobile Web segment', r'in the Mobile Web segment'),
]

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or '.venv' in root:
        continue
    for file in files:
        if not file.endswith(('.py', '.json', '.md', '.txt', '.ps1')):
            continue
        filepath = os.path.join(root, file)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            original_content = content
            for old, new in replacements:
                content = re.sub(old, new, content, flags=re.IGNORECASE)
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {filepath}')
        except Exception as e:
            pass
