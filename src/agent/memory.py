"""Memory module — tracks conversation + tool result history."""

from typing import Any, Dict, List, Optional
from datetime import datetime


class ConversationMemory:
    """
    Maintains conversation history and tool results.
    
    Tracks:
    - User messages
    - Assistant responses
    - Tool calls and results
    - Iteration history
    """
    
    def __init__(self):
        """Initialize conversation memory."""
        self.messages: List[Dict[str, Any]] = []
        self.tool_results: Dict[str, List[Any]] = {}
        self.created_at = datetime.now()
    
    def add_user_message(self, content: str):
        """
        Add user message to history.
        
        Args:
            content: User's message text
        """
        self.messages.append({
            "role": "user",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_assistant_message(self, content: Dict[str, Any]):
        """
        Add assistant response to history.
        
        Args:
            content: Assistant's response
        """
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_tool_result(self, tool_name: str, result: Any):
        """
        Add tool execution result to history.
        
        Args:
            tool_name: Name of the tool executed
            result: Result from tool execution
        """
        if tool_name not in self.tool_results:
            self.tool_results[tool_name] = []
        
        self.tool_results[tool_name].append({
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Also add to messages for context
        self.messages.append({
            "role": "tool",
            "tool_name": tool_name,
            "content": str(result),
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Returns:
            List of messages
        """
        return self.messages.copy()
    
    def reset(self):
        """Clear conversation history."""
        self.messages = []
        self.tool_results = {}
        self.created_at = datetime.now()
