"""Base tool classes and decorators."""

from typing import Any, Callable, Dict, Optional
from functools import wraps


class ToolRegistry:
    """Registry for managing available tools."""
    
    _tools: Dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str, schema: Optional[Dict[str, Any]] = None):
        """
        Register a tool in the registry.
        
        Args:
            name: Tool name
            schema: Tool schema for LLM
        """
        def decorator(func: Callable) -> Callable:
            func.schema = schema or {
                "name": name,
                "description": func.__doc__ or "",
                "input_schema": {"type": "object", "properties": {}},
            }
            cls._tools[name] = func
            return func
        return decorator
    
    @classmethod
    def get_tools(cls) -> Dict[str, Callable]:
        """Get all registered tools."""
        return cls._tools.copy()
    
    @classmethod
    def get_tool(cls, name: str) -> Optional[Callable]:
        """Get a specific tool by name."""
        return cls._tools.get(name)


def tool(
    name: str,
    description: str = "",
    input_schema: Optional[Dict[str, Any]] = None,
):
    """
    Decorator to register a function as a tool.
    
    Args:
        name: Tool name
        description: Tool description for LLM
        input_schema: JSON schema for tool inputs
    """
    def decorator(func: Callable) -> Callable:
        schema = {
            "name": name,
            "description": description or func.__doc__ or "",
            "input_schema": input_schema or {"type": "object", "properties": {}},
        }
        func.schema = schema
        ToolRegistry.register(name, schema)(func)
        return func
    return decorator
