"""
memory.py — Tracks the full conversation history for a single agent run.

The Anthropic API requires that assistant tool-use turns and their
corresponding tool_result turns appear consecutively in the message list.
This class handles that bookkeeping automatically.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from src.llm.client import ToolCall, LLMClient


@dataclass
class Memory:
    """Append-only message history for one agent session."""

    messages: list[dict] = field(default_factory=list)

    def add_user(self, text: str) -> None:
        self.messages.append(LLMClient.user_message(text))

    def add_assistant_text(self, text: str) -> None:
        if text.strip():
            self.messages.append(LLMClient.assistant_message(text))

    def add_assistant_tool_calls(self, tool_calls: list[ToolCall], text: str = "") -> None:
        """
        Add the assistant turn that contains tool_use blocks.
        Must be followed by add_tool_results() before the next LLM call.
        """
        self.messages.append(
            LLMClient.assistant_tool_call_message(tool_calls, text)
        )

    def add_tool_results(self, tool_calls: list[ToolCall], results: list[str]) -> None:
        """
        Add all tool results for a batch of tool calls.
        Anthropic requires a single user message containing ALL tool_result
        blocks from the preceding assistant tool_use turn.
        """
        content_blocks = [
            {
                "type": "tool_result",
                "tool_use_id": tc.id,
                "content": result,
            }
            for tc, result in zip(tool_calls, results)
        ]
        self.messages.append({"role": "user", "content": content_blocks})

    def snapshot(self) -> list[dict]:
        """Return a copy of the current message list."""
        return list(self.messages)

    def clear(self) -> None:
        self.messages.clear()

    def __len__(self) -> int:
        return len(self.messages)