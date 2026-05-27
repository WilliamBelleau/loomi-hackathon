import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
except ImportError:
    print("Error: The 'mcp' package is not installed. Please run:")
    print("pip install -r requirements-mcp.txt")
    sys.exit(1)

DATA_DIR = Path(__file__).parent.parent / "data"
SNAPSHOT_FILE = DATA_DIR / "live_evidence_snapshot.json"

async def refresh_snapshot():
    mcp_url = os.environ.get("LOOMI_MCP_ANALYTICS_MARKETING_URL")
    if not mcp_url:
        print("Error: LOOMI_MCP_ANALYTICS_MARKETING_URL environment variable is not set.")
        print("Please set it to the Bloomreach Analytics MCP endpoint to refresh the snapshot.")
        sys.exit(1)
        
    print(f"Connecting to {mcp_url} ...")
    
    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "project_display_name": "Unknown Sandbox",
        "capture_method": "scripts/refresh_mcp_snapshot.py",
        "source": "LOOMI_MCP_ANALYTICS_MARKETING_URL",
        "checkout_trend": [],
        "cart_trend": [],
        "funnel_overall": {},
        "funnel_mobile": {},
        "campaign_activity": [],
        "device_breakdown": {},
        "queries_attempted": 0,
        "queries_succeeded": 0,
        "errors": []
    }
    
    try:
        async with sse_client(mcp_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Session initialized.")
                
                queries = [
                    ("checkout_trend", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='checkout' AND timestamp >= now() - 14d GROUP BY date"}),
                    ("cart_trend", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='cart_update' AND timestamp >= now() - 14d GROUP BY date"}),
                    ("funnel_overall", "get_funnel", {"funnel_id": "session_to_checkout"}),
                    ("funnel_mobile", "get_funnel", {"funnel_id": "mobile_session_to_checkout"}),
                    ("campaign_activity", "execute_analytics_eql", {"query": "SELECT count() FROM campaigns WHERE timestamp >= now() - 14d GROUP BY date, action_type"}),
                    ("device_breakdown", "execute_analytics_eql", {"query": "SELECT count() FROM events WHERE name='session_start' GROUP BY device"})
                ]
                
                for idx, (intent, tool_name, params) in enumerate(queries):
                    snapshot["queries_attempted"] += 1
                    try:
                        print(f"Executing query [{intent}] via {tool_name}...")
                        # This will likely fail with a schema validation or tool not found error,
                        # but we structure it correctly according to plan rules.
                        result = await session.call_tool(tool_name, params)
                        snapshot[intent] = result.content
                        snapshot["queries_succeeded"] += 1
                        print(f"  Success: {intent}")
                    except Exception as e:
                        print(f"  Failed: {intent} - {e}")
                        snapshot["errors"].append(f"{intent} failed: {str(e)}")
                        
                    if idx < len(queries) - 1:
                        print("Rate limiting: sleeping for 15 seconds...")
                        await asyncio.sleep(15)
                
                DATA_DIR.mkdir(exist_ok=True)
                SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))
                print(f"\nSnapshot successfully written to {SNAPSHOT_FILE}")
                
    except Exception as e:
        print(f"Failed to connect or initialize session: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(refresh_snapshot())
