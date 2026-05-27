"""
discover_mcp_tools.py — Standalone Bloomreach Loomi Connect MCP Discovery Script.

Purpose:
    List available tools from the Bloomreach Loomi Connect MCP server.
    Used to confirm real tool names and schemas before writing any live adapter code.

Usage:
    1. Set environment variables (see .env.example for variable names):
           export LOOMI_MCP_ANALYTICS_MARKETING_URL="<url from Bloomreach sandbox portal>"
           export LOOMI_MCP_AUTH_MODE="browser"          # default; change only if confirmed
           export LOOMI_MCP_TOKEN="<token>"              # only if programmatic auth confirmed

    2. Run:
           python scripts/discover_mcp_tools.py

    3. Output is saved (sanitized) to:
           scripts/mcp_discovery_output.json  (gitignored)

Important constraints:
    - This script is STANDALONE. It is not imported by the app, agent, or tools packages.
    - It is not required by tests. Tests never call this script.
    - It does NOT affect mock-first behavior. LOOMI_MCP_LIVE is not read here.
    - All URLs and tokens are masked in terminal output and in the saved output file.
    - No raw credentials, raw tokens, or full endpoint URLs are ever written to disk.
    - If programmatic auth is not available (browser-auth-only), the script exits
      cleanly with a clear message rather than pretending to work.

Limitations:
    - Loomi Connect MCP uses Streamable HTTP transport with browser-based auth.
    - Token-based programmatic access is TBD / unconfirmed by Bloomreach.
    - If LOOMI_MCP_AUTH_MODE=browser and no token is present, the script will
      explain why it cannot connect programmatically and suggest alternatives.
    - Do not modify this script to hardcode any URL or credential.

Output file:
    scripts/mcp_discovery_output.json — gitignored, sanitized (no raw secrets or URLs).
    If the file already exists, it is overwritten.
"""
from __future__ import annotations

import json
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — read from environment only, never hardcoded
# ---------------------------------------------------------------------------

ANALYTICS_MARKETING_URL: str | None = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL")
CONVERSATIONS_URL: str | None = os.environ.get("LOOMI_MCP_CONVERSATIONS_URL")
AUTH_MODE: str = os.environ.get("LOOMI_MCP_AUTH_MODE", "browser").lower().strip()
TOKEN: str | None = os.environ.get("LOOMI_MCP_TOKEN")

OUTPUT_PATH = Path(__file__).parent / "mcp_discovery_output.json"


# ---------------------------------------------------------------------------
# Masking helpers — never log raw secrets
# ---------------------------------------------------------------------------

def _mask_url(url: str | None) -> str:
    """Return a masked representation of a URL for safe terminal/file output.

    Preserves the scheme (https://) and replaces the rest with ***.
    Example: 'https://sandbox.example.com/mcp/v1' → 'https://***'
    """
    if not url:
        return "(not set)"
    scheme_end = url.find("://")
    if scheme_end == -1:
        return "***"
    return url[: scheme_end + 3] + "***"


def _mask_token(token: str | None) -> str:
    """Return a masked representation of a token for safe terminal/file output.

    Shows first 4 + *** + last 2 characters if long enough, otherwise ***.
    """
    if not token:
        return "(not set)"
    if len(token) >= 10:
        return token[:4] + "***" + token[-2:]
    return "***"


def _sanitize_output(data: dict) -> dict:
    """Return a copy of data safe for disk — all URLs and tokens replaced with masks."""
    sanitized = json.loads(json.dumps(data))  # deep copy via round-trip
    sanitized["endpoints"]["analytics_marketing_url"] = _mask_url(ANALYTICS_MARKETING_URL)
    sanitized["endpoints"]["conversations_url"] = _mask_url(CONVERSATIONS_URL)
    if "token_hint" in sanitized.get("auth", {}):
        sanitized["auth"]["token_hint"] = _mask_token(TOKEN)
    return sanitized


# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

def _check_environment() -> list[str]:
    """Return a list of problems found in the environment. Empty = ready to proceed."""
    problems: list[str] = []

    if not ANALYTICS_MARKETING_URL and not CONVERSATIONS_URL:
        problems.append(
            "No MCP endpoint URLs are set. Set at least one of:\n"
            "  LOOMI_MCP_ANALYTICS_MARKETING_URL\n"
            "  LOOMI_MCP_CONVERSATIONS_URL\n"
            "Values come from the Bloomreach sandbox portal (shared via Slack)."
        )

    if AUTH_MODE not in ("browser", "token"):
        problems.append(
            f"LOOMI_MCP_AUTH_MODE='{AUTH_MODE}' is not recognized. "
            "Use 'browser' (default) or 'token' (only if confirmed by Bloomreach)."
        )

    if AUTH_MODE == "token" and not TOKEN:
        problems.append(
            "LOOMI_MCP_AUTH_MODE=token requires LOOMI_MCP_TOKEN to be set.\n"
            "Only configure this if Bloomreach has confirmed programmatic token auth works."
        )

    return problems


def _explain_browser_auth_limitation() -> str:
    return textwrap.dedent("""
        ┌─────────────────────────────────────────────────────────────────────┐
        │  Programmatic Discovery Not Available (Browser Auth Mode)           │
        ├─────────────────────────────────────────────────────────────────────┤
        │                                                                     │
        │  LOOMI_MCP_AUTH_MODE=browser (default).                             │
        │                                                                     │
        │  Loomi Connect MCP uses browser-based Bloomreach authentication.    │
        │  This means a human must authenticate in a browser session first,   │
        │  and an MCP client (Claude Desktop, Cursor) holds the session.      │
        │  A standalone Python script cannot complete this flow automatically. │
        │                                                                     │
        │  OPTIONS:                                                            │
        │  1. Connect via a supported MCP client (Claude Desktop / Cursor)    │
        │     and use the client's tool inspector to list available tools.    │
        │     Record the tool names in docs/mcp-integration-plan.md.          │
        │                                                                     │
        │  2. Ask Bloomreach if a session token can be extracted after        │
        │     browser-auth and used for programmatic access.                  │
        │     If yes: set LOOMI_MCP_AUTH_MODE=token and LOOMI_MCP_TOKEN=...  │
        │     then re-run this script.                                        │
        │                                                                     │
        │  3. If Bloomreach provides an API key or OAuth client credentials   │
        │     for sandbox use, update this script accordingly and document    │
        │     the method in docs/mcp-integration-plan.md.                    │
        │                                                                     │
        │  NEXT STEP: Check the hackathon Slack for auth details.             │
        └─────────────────────────────────────────────────────────────────────┘
    """).strip()


# ---------------------------------------------------------------------------
# Discovery attempt — only runs if auth mode is token
# ---------------------------------------------------------------------------

def _attempt_token_discovery(url: str, label: str) -> dict:
    """
    Attempt to connect to a Loomi Connect MCP endpoint using a bearer token
    and list available tools.

    Returns a dict with 'success', 'tools', and 'error' keys.
    Never logs or saves the raw token or raw URL.

    Note: This uses only stdlib (urllib) to avoid adding new dependencies.
    If the mcp package is available and preferred, replace this with an
    mcp.ClientSession call — but do not add mcp to requirements.txt until
    Phase D.2 is approved.
    """
    import urllib.error
    import urllib.request

    result: dict = {
        "endpoint_label": label,
        "endpoint_masked": _mask_url(url),
        "success": False,
        "tools": [],
        "error": None,
    }

    # MCP initialize request per Streamable HTTP transport spec.
    # The exact path segment may differ — adjust based on discovery findings.
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "loomi-discover", "version": "0.1.0"},
        },
    }

    tools_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/json, text/event-stream",
    }

    try:
        # Step 1: initialize
        req = urllib.request.Request(
            url,
            data=json.dumps(init_payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            init_body = resp.read().decode()

        # Step 2: list tools
        req2 = urllib.request.Request(
            url,
            data=json.dumps(tools_payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req2, timeout=10) as resp2:
            tools_body = resp2.read().decode()

        # Parse — handle both plain JSON and SSE (text/event-stream) responses
        tools_text = tools_body
        if tools_text.startswith("data:"):
            # SSE: extract the first data line
            for line in tools_text.splitlines():
                if line.startswith("data:"):
                    tools_text = line[len("data:"):].strip()
                    break

        tools_response = json.loads(tools_text)

        if "result" in tools_response and "tools" in tools_response["result"]:
            tools_raw = tools_response["result"]["tools"]
            result["success"] = True
            result["tools"] = [
                {
                    "name": t.get("name", "unknown"),
                    "description": t.get("description", ""),
                    # Include inputSchema summary but not full schema to keep output readable.
                    "input_schema_keys": list(
                        t.get("inputSchema", {}).get("properties", {}).keys()
                    ),
                }
                for t in tools_raw
            ]
        else:
            result["error"] = (
                f"Unexpected tools/list response structure. "
                f"Keys found: {list(tools_response.keys())}"
            )

    except urllib.error.HTTPError as exc:
        result["error"] = f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        result["error"] = f"Connection error: {exc.reason}"
    except json.JSONDecodeError as exc:
        result["error"] = f"JSON parse error: {exc}"
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"Unexpected error: {type(exc).__name__}: {exc}"

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the discovery script. Returns exit code (0 = success or informative, 1 = error)."""

    print("=" * 70)
    print("Loomi Connect MCP Discovery Script")
    print("Simons Unified Commerce Signal Agent — Phase D.1")
    print("=" * 70)
    print()

    # --- Pre-flight ---
    problems = _check_environment()
    if problems:
        print("⛔ Cannot proceed — environment not configured:\n")
        for p in problems:
            for line in p.splitlines():
                print(f"   {line}")
            print()
        print("See .env.example for variable names.")
        print("See docs/mcp-integration-plan.md for setup guidance.")
        print()
        return 1

    print(f"Auth mode:          {AUTH_MODE}")
    print(f"Analytics/Mktg URL: {_mask_url(ANALYTICS_MARKETING_URL)}")
    print(f"Conversations URL:  {_mask_url(CONVERSATIONS_URL)}")
    if TOKEN:
        print(f"Token hint:         {_mask_token(TOKEN)}")
    print()

    # --- Browser auth path: explain limitation and exit cleanly ---
    if AUTH_MODE == "browser":
        print(_explain_browser_auth_limitation())
        print()

        # Save a summary record so there is a gitignored artifact showing the attempt.
        summary = {
            "script": "discover_mcp_tools.py",
            "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
            "auth_mode": "browser",
            "result": "skipped — programmatic discovery not possible with browser auth mode",
            "endpoints": {
                "analytics_marketing_url": _mask_url(ANALYTICS_MARKETING_URL),
                "conversations_url": _mask_url(CONVERSATIONS_URL),
            },
            "tools_found": [],
            "next_steps": [
                "Use a supported MCP client (Claude Desktop / Cursor) to list tools manually.",
                "Record confirmed tool names in docs/mcp-integration-plan.md.",
                "Ask Bloomreach if a session token can be used for programmatic access.",
                "If token access is confirmed, set LOOMI_MCP_AUTH_MODE=token and re-run.",
            ],
        }
        OUTPUT_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"ℹ️  Summary saved (sanitized) to: {OUTPUT_PATH.name}")
        print("   (This file is gitignored. It contains no secrets.)")
        return 0

    # --- Token auth path: attempt live discovery ---
    print("Attempting tool discovery with token auth...\n")

    all_results: list[dict] = []

    endpoints_to_try: list[tuple[str, str]] = []
    if ANALYTICS_MARKETING_URL:
        endpoints_to_try.append((ANALYTICS_MARKETING_URL, "analytics_marketing"))
    if CONVERSATIONS_URL:
        endpoints_to_try.append((CONVERSATIONS_URL, "conversations"))

    for url, label in endpoints_to_try:
        print(f"  → Querying: {label} ({_mask_url(url)}) ...", end=" ", flush=True)
        result = _attempt_token_discovery(url, label)
        if result["success"]:
            print(f"✅ {len(result['tools'])} tool(s) found")
            for tool in result["tools"]:
                print(f"       Tool: {tool['name']}")
                if tool["description"]:
                    desc_short = tool["description"][:80].rstrip()
                    print(f"         └─ {desc_short}")
        else:
            print(f"❌ {result['error']}")
        all_results.append(result)
        print()

    # --- Save sanitized output ---
    output = {
        "script": "discover_mcp_tools.py",
        "timestamp_utc": datetime.now(tz=timezone.utc).isoformat(),
        "auth_mode": "token",
        "auth": {"token_hint": _mask_token(TOKEN)},
        "endpoints": {
            "analytics_marketing_url": _mask_url(ANALYTICS_MARKETING_URL),
            "conversations_url": _mask_url(CONVERSATIONS_URL),
        },
        "discovery_results": all_results,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"💾 Discovery output saved (sanitized) to: {OUTPUT_PATH.name}")
    print("   (This file is gitignored. It contains no raw URLs or tokens.)")
    print()

    success_count = sum(1 for r in all_results if r["success"])
    print(f"Summary: {success_count}/{len(all_results)} endpoint(s) responded successfully.")

    if success_count > 0:
        print()
        print("Next steps:")
        print("  1. Review the tool names in the output file.")
        print("  2. Update docs/mcp-integration-plan.md with confirmed tool names.")
        print("  3. Proceed to Phase D.2 (feature-flagged live adapter) once schema is confirmed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
