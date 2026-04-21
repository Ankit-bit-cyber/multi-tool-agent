"""
client.py — Thin abstraction over the Anthropic messages API.

Provides:
  - LLMClient.chat()          — single completion (direct mode)
  - LLMClient.chat_with_tools() — completion with tool schemas attached
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import anthropic

from config.settings import settings


# ── Response dataclasses ──────────────────────────────────────────────────────

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str                          # text content (may be empty if tool_calls present)
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""                 # "end_turn" | "tool_use" | "max_tokens"

    @property
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


# ── LLMClient ─────────────────────────────────────────────────────────────────

class LLMClient:
    """Wraps the Anthropic SDK for both direct and tool-augmented calls."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.llm_model
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # ── direct chat ───────────────────────────────────────────────────────────

    def chat(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Send a plain chat request (no tools). Used for direct-LLM comparison."""
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )
        if system:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)
        text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )
        return LLMResponse(
            content=text,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "",
        )

    # ── chat with tools ───────────────────────────────────────────────────────

    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        system: str = "",
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """
        Send a chat request with tool schemas.
        Returns an LLMResponse; if stop_reason == 'tool_use',
        .tool_calls will be populated.
        """
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools,
        )
        if system:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)

        text_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input if isinstance(block.input, dict) else {},
                    )
                )

        return LLMResponse(
            content="\n".join(text_parts),
            tool_calls=tool_calls,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason or "",
        )

    # ── raw message list helpers ──────────────────────────────────────────────

    @staticmethod
    def user_message(text: str) -> dict:
        return {"role": "user", "content": text}

    @staticmethod
    def assistant_message(text: str) -> dict:
        return {"role": "assistant", "content": text}

    @staticmethod
    def tool_result_message(tool_use_id: str, result: str) -> dict:
        """Wrap a tool result in the format Anthropic expects."""
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": result,
                }
            ],
        }

    @staticmethod
    def assistant_tool_call_message(tool_calls: list[ToolCall], text: str = "") -> dict:
        """
        Build the assistant message that contains tool_use blocks,
        matching what the Anthropic API actually returned.
        """
        content: list[dict] = []
        if text:
            content.append({"type": "text", "text": text})
        for tc in tool_calls:
            content.append(
                {
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.name,
                    "input": tc.arguments,
                }
            )
        return {"role": "assistant", "content": content}