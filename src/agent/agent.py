"""Main Agent class — orchestration loop."""

from typing import Any, Dict, List, Optional
from src.llm.client import LLMClient
from .memory import ConversationMemory
from .router import Router
from .executor import Executor


class Agent:
    """
    Main orchestration loop for multi-tool agent.
    
    Coordinates:
    - LLM inference
    - Tool routing
    - Tool execution
    - Memory management
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        tools_registry: Dict[str, Any],
        max_iterations: int = 10,
        verbose: bool = True,
    ):
        """
        Initialize the Agent.
        
        Args:
            llm_client: LLM client instance (Anthropic/OpenAI)
            tools_registry: Dictionary of available tools
            max_iterations: Maximum number of agent loop iterations
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.tools_registry = tools_registry
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        self.memory = ConversationMemory()
        self.router = Router(llm_client)
        self.executor = Executor(tools_registry)
    
    def run(self, user_query: str) -> str:
        """
        Run the agent loop.
        
        Args:
            user_query: User's input query
            
        Returns:
            Final response from the agent
        """
        self.memory.add_user_message(user_query)
        
        for iteration in range(self.max_iterations):
            if self.verbose:
                print(f"\n--- Iteration {iteration + 1} ---")
            
            # Get LLM response
            response = self.llm_client.complete(
                messages=self.memory.get_messages(),
                tools=self.executor.get_tool_schemas(),
            )
            
            # Check if tool call or final response
            if response.get("type") == "tool_use":
                # Route to appropriate tool
                tool_name = response.get("tool_name")
                tool_input = response.get("tool_input", {})
                
                if self.verbose:
                    print(f"Calling tool: {tool_name}")
                
                # Execute tool
                result = self.executor.execute(tool_name, **tool_input)
                
                # Add to memory
                self.memory.add_assistant_message(response)
                self.memory.add_tool_result(tool_name, result)
                
            else:
                # Final response
                final_text = response.get("text", "")
                self.memory.add_assistant_message(response)
                return final_text
        
        return "Max iterations reached without final response."
    
    def reset(self):
        """Reset agent memory and state."""
        self.memory.reset()
