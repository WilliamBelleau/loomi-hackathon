param(
    [ValidateSet("Demo", "Live", "Cache")]
    [string]$Mode = "Demo",

    [ValidateSet("None", "Triage", "Refresh", "RefreshThenTriage")]
    [string]$Autorun = "None",

    [switch]$RunTests,
    [switch]$SecretsScan,
    [switch]$OpenBrowser,
    [switch]$Presentation
)

Write-Host "=========================================="
Write-Host " Simons Unified Commerce Signal Agent"
Write-Host " Demo Autopilot Mode"
Write-Host "=========================================="

# 1. Validate Python
try {
    $pythonVer = python --version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Python not found" }
} catch {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# 2. Validate Streamlit
try {
    $stVer = python -m streamlit version 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Streamlit not found" }
} catch {
    Write-Error "Streamlit is not installed in the current Python environment."
    exit 1
}

# 3. Validate Live MCP dependencies
if ($Mode -eq "Live") {
    # Check node
    try {
        $nodeVer = node --version 2>&1
        if ($LASTEXITCODE -ne 0) { throw "Node not found" }
    } catch {
        Write-Error "Node/npx is required for Live Mode but is not installed or not in PATH."
        exit 1
    }

    # Check env vars
    $url = $env:LOOMI_MCP_ANALYTICS_MARKETING_URL
    $projectId = $env:LOOMI_MCP_PROJECT_ID
    if ([string]::IsNullOrWhiteSpace($url) -or [string]::IsNullOrWhiteSpace($projectId)) {
        Write-Error "Live mode requires both LOOMI_MCP_ANALYTICS_MARKETING_URL and LOOMI_MCP_PROJECT_ID env vars."
        exit 1
    }
}

# 4. Optionally Run Tests
if ($RunTests) {
    Write-Host "`n[+] Running pytest..."
    python -m pytest -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed. Aborting."
        exit 1
    }
}

# 5. Optionally Run Secrets Scan
if ($SecretsScan) {
    Write-Host "`n[+] Running secrets scan..."
    git grep -n "CLIENT_SECRET\|PASSWORD\|API_KEY\|TOKEN\|sb-\|sandbox.paypal\|loomi-mcp-alpha\|952be3a0" .
    if ($LASTEXITCODE -eq 0) {
        Write-Error "Secrets scan found potential matches. Please resolve. Aborting."
        exit 1
    } else {
        Write-Host "Secrets scan passed."
    }
}

# 6. Start Streamlit and Open Browser
Write-Host "`n[+] Starting Streamlit UI in Demo Autopilot Mode..."

$presentationFlag = if ($Presentation) { "1" } else { "0" }

$urlPath = "http://localhost:8501/?demo_mode=$($Mode.ToLower())&autorun=$($Autorun.ToLower())&presentation=$presentationFlag"

if ($OpenBrowser) {
    Write-Host "[+] Opening browser to: $urlPath"
    Start-Process $urlPath
    # Start streamlit without opening a browser automatically
    python -m streamlit run app/ui_streamlit.py --server.headless true
} else {
    Write-Host "[+] Please open your browser to: $urlPath"
    python -m streamlit run app/ui_streamlit.py
}
