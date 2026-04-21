"""
executor.py — Executes tool calls and returns results as strings.
"""

from __future__ import annotations
import traceback
from typing import Any

from src.tools.base import ToolRegistry
from src.llm.client import ToolCall


class ToolExecutor:
    """
    Executes tool calls against a ToolRegistry.
    All exceptions are caught and returned as error strings so the
    agent loop is never interrupted by a failing tool.
    """

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def run(self, tool_call: ToolCall) -> str:
        """Execute a single tool call. Returns a string result (never raises)."""
        tool_name = tool_call.name
        args = tool_call.arguments

        if tool_name not in self.registry.names():
            return (
                f"Error: tool '{tool_name}' is not registered. "
                f"Available tools: {', '.join(self.registry.names())}"
            )

        try:
            result = self.registry.execute(tool_name, **args)
            return str(result)
        except TypeError as exc:
            return f"Error: wrong arguments for '{tool_name}': {exc}"
        except Exception:
            return (
                f"Error executing '{tool_name}':\n"
                + traceback.format_exc(limit=3)
            )

    def run_all(self, tool_calls: list[ToolCall]) -> list[str]:
        """Execute a list of tool calls and return results in order."""
        return [self.run(tc) for tc in tool_calls]