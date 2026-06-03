import re
with open('docs/demo-script.md', 'r', encoding='utf-8') as f:
    c = f.read()

old = r'> To complete the omnichannel triage scenario, the Ops and Conversations data are synthetic fixtures—representing internal retailer systems like Datadog or OMS that don\'t exist in the Bloomreach sandbox."'
new = r'> "The sandbox supports mobile funnel and campaign analytics. Payment and detailed ops signals are modeled as synthetic external commerce-system signals."'
c = c.replace(old, new)

with open('docs/demo-script.md', 'w', encoding='utf-8') as f:
    f.write(c)
