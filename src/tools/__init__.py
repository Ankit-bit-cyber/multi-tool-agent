from src.tools.base import tool, ToolRegistry, ToolDefinition
from src.tools.calculator import calculator
from src.tools.weather import weather
from src.tools.search import search


def build_registry() -> ToolRegistry:
    """Create and return a ToolRegistry populated with all available tools."""
    registry = ToolRegistry()
    registry.register(calculator)
    registry.register(weather)
    registry.register(search)
    return registry


__all__ = [
    "tool",
    "ToolRegistry",
    "ToolDefinition",
    "calculator",
    "weather",
    "search",
    "build_registry",
]