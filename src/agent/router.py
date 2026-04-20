"""Router module — decides which tool the LLM should call."""

from typing import Dict, Any, Optional
from src.llm.client import LLMClient


class Router:
    """
    Routes LLM outputs to appropriate tools.
    
    Responsibilities:
    - Parse LLM responses for tool calls
    - Validate tool existence
    - Prioritize tools based on context
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize Router.
        
        Args:
            llm_client: LLM client for tool selection logic
        """
        self.llm_client = llm_client
    
    def route(self, llm_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route LLM response to a tool.
        
        Args:
            llm_response: Response from LLM
            
        Returns:
            Tool call specification or None if no tool needed
        """
        if llm_response.get("type") != "tool_use":
            return None
        
        return {
            "tool_name": llm_response.get("tool_name"),
            "tool_input": llm_response.get("tool_input", {}),
        }
    
    def get_available_tools(self, tools_registry: Dict[str, Any]) -> list:
        """
        Get list of available tools for routing context.
        
        Args:
            tools_registry: Registry of available tools
            
        Returns:
            List of tool names
        """
        return list(tools_registry.keys())
