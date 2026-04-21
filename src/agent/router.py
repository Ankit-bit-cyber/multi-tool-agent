"""
router.py — Decides whether the LLM response requires a tool call
or is a final answer. Pure logic, no API calls.
"""

from __future__ import annotations
from src.llm.client import LLMResponse


class ToolRouter:
    """
    Inspects an LLMResponse and classifies it as:
      - tool_call   → LLM wants to invoke one or more tools
      - final_answer → LLM produced a plain text answer
    """

    def route(self, response: LLMResponse) -> str:
        if response.has_tool_calls:
            return "tool_call"
        return "final_answer"

    def is_tool_call(self, response: LLMResponse) -> bool:
        return self.route(response) == "tool_call"

    def is_final_answer(self, response: LLMResponse) -> bool:
        return self.route(response) == "final_answer"