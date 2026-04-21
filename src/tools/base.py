"""
base.py — @tool decorator and ToolRegistry.

Usage:
    @tool(name="my_tool", description="Does something useful")
    def my_tool(x: int, y: str) -> str:
        ...

    registry = ToolRegistry()
    registry.register(my_tool)
    schema = registry.get_schema()   # list[dict] ready for the LLM
"""

from __future__ import annotations

import inspect
import functools
from dataclasses import dataclass, field
from typing import Any, Callable, get_type_hints


# ── Type → JSON-schema primitive map ─────────────────────────────────────────

_PY_TO_JSON: dict[Any, str] = {
    int: "number",
    float: "number",
    str: "string",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _python_type_to_json(annotation: Any) -> str:
    return _PY_TO_JSON.get(annotation, "string")


# ── ToolDefinition ────────────────────────────────────────────────────────────

@dataclass
class ToolDefinition:
    name: str
    description: str
    func: Callable
    parameters: dict = field(default_factory=dict)   # JSON-schema properties
    required: list[str] = field(default_factory=list)

    def to_anthropic_schema(self) -> dict:
        """Return the tool dict expected by the Anthropic messages API."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required,
            },
        }

    def to_openai_schema(self) -> dict:
        """Return the tool dict expected by the OpenAI chat-completions API."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                },
            },
        }

    def call(self, **kwargs: Any) -> Any:
        return self.func(**kwargs)


# ── @tool decorator ───────────────────────────────────────────────────────────

def tool(
    name: str | None = None,
    description: str = "",
    param_descriptions: dict[str, str] | None = None,
):
    """
    Decorator that wraps a function and attaches a ToolDefinition to it.

    @tool(name="calculator", description="Evaluates a math expression.")
    def calculator(expression: str) -> str:
        ...
    """
    param_descriptions = param_descriptions or {}

    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_desc = description or (inspect.getdoc(func) or "")

        # Build JSON-schema properties from type hints
        hints = get_type_hints(func)
        sig = inspect.signature(func)
        properties: dict[str, dict] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
            annotation = hints.get(param_name, str)
            prop: dict[str, str] = {
                "type": _python_type_to_json(annotation),
                "description": param_descriptions.get(param_name, f"The {param_name} parameter"),
            }
            properties[param_name] = prop
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        definition = ToolDefinition(
            name=tool_name,
            description=tool_desc,
            func=func,
            parameters=properties,
            required=required,
        )

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper._tool_definition = definition  # type: ignore[attr-defined]
        return wrapper

    return decorator


# ── ToolRegistry ──────────────────────────────────────────────────────────────

class ToolRegistry:
    """Holds all registered tools and provides schema + dispatch."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, func: Callable) -> None:
        """Register a function decorated with @tool."""
        if not hasattr(func, "_tool_definition"):
            raise ValueError(f"{func.__name__} is not decorated with @tool")
        defn: ToolDefinition = func._tool_definition
        self._tools[defn.name] = defn

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools.keys())

    def anthropic_schemas(self) -> list[dict]:
        return [t.to_anthropic_schema() for t in self._tools.values()]

    def openai_schemas(self) -> list[dict]:
        return [t.to_openai_schema() for t in self._tools.values()]

    def execute(self, name: str, **kwargs: Any) -> Any:
        return self.get(name).call(**kwargs)

    def __len__(self) -> int:
        return len(self._tools)

    def __repr__(self) -> str:
        return f"ToolRegistry(tools={self.names()})"
