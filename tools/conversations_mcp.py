"""
conversations_mcp.py — Conversations MCP Adapter (MOCKED).

Current state: loads synthetic fixture data from data/conversation_intents.json.

Phase 2 replacement:
  Replace the body of get_intent_signals() with a real Bloomreach Conversations
  MCP tool call. The method signature and return type do not change.
  Example (placeholder — exact tool name/schema TBD by Bloomreach):

    # result = await session.call_tool("loomi_conversations_get_intent_trends", {...})
    # return [ConversationSignal(**item) for item in result["intents"]]

No network calls are made in the current implementation.
"""
from __future__ import annotations

import json
from pathlib import Path

from agent.schemas import ConversationSignal

_FIXTURE_PATH = Path(__file__).parent.parent / "data" / "conversation_intents.json"


class ConversationsMCPClient:
    """
    Adapter for the Bloomreach Loomi Connect Conversations MCP.

    MOCKED: Returns synthetic fixture data.
    Replace get_intent_signals() body with real MCP call once Bloomreach
    provides sandbox credentials, endpoint, and tool schema.
    """

    def get_intent_signals(self) -> list[ConversationSignal]:
        """Return a list of rising customer friction intents."""
        raw = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
        return [ConversationSignal(**item) for item in raw]
