"""Executor module — executes tool calls and handles errors."""

from typing import Any, Dict, Optional
from src.logging.logger import VerboseLogger


class Executor:
    """
    Executes tool calls with error handling.
    
    Responsibilities:
    - Validate tool calls
    - Execute with proper error handling
    - Return structured results
    """
    
    def __init__(self, tools_registry: Dict[str, Any]):
        """
        Initialize Executor.
        
        Args:
            tools_registry: Registry of available tools
        """
        self.tools_registry = tools_registry
        self.logger = VerboseLogger()
    
    def execute(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool call.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if tool_name not in self.tools_registry:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        
        tool_callable = self.tools_registry[tool_name]
        
        try:
            self.logger.log(f"Executing tool: {tool_name} with args: {kwargs}")
            result = tool_callable(**kwargs)
            self.logger.log(f"Tool result: {result}")
            return result
        except Exception as e:
            self.logger.log(f"Tool execution error: {str(e)}")
            raise
    
    def get_tool_schemas(self) -> list:
        """
        Get tool schemas for LLM.
        
        Returns:
            List of tool schemas
        """
        schemas = []
        for tool_name, tool_callable in self.tools_registry.items():
            schema = getattr(tool_callable, "schema", None)
            if schema:
                schemas.append(schema)
        return schemas
