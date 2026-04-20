"""LLM client abstraction — Anthropic/OpenAI support."""

import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Get LLM completion.
        
        Args:
            messages: Conversation history
            tools: Available tools
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            
        Returns:
            LLM response
        """
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude LLM client."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Anthropic client.
        
        Args:
            model: Model name to use
        """
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed")
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Get completion from Claude."""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
            }
            
            if tools:
                kwargs["tools"] = tools
            
            response = self.client.messages.create(**kwargs)
            
            # Parse response
            content = response.content[0] if response.content else {}
            
            if hasattr(content, "type") and content.type == "tool_use":
                return {
                    "type": "tool_use",
                    "tool_name": content.name,
                    "tool_input": content.input,
                }
            else:
                return {
                    "type": "text",
                    "text": getattr(content, "text", str(content)),
                }
        except Exception as e:
            return {"error": f"Claude API error: {str(e)}"}


class OpenAIClient(LLMClient):
    """OpenAI GPT LLM client."""
    
    def __init__(self, model: str = "gpt-4-turbo"):
        """
        Initialize OpenAI client.
        
        Args:
            model: Model name to use
        """
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI()
        except ImportError:
            raise ImportError("openai package not installed")
    
    def complete(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Get completion from GPT."""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
            }
            
            if tools:
                # Convert tools to OpenAI format
                kwargs["tools"] = [
                    {"type": "function", "function": tool} for tool in tools
                ]
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Parse response
            choice = response.choices[0]
            
            if choice.message.tool_calls:
                tool_call = choice.message.tool_calls[0]
                return {
                    "type": "tool_use",
                    "tool_name": tool_call.function.name,
                    "tool_input": eval(tool_call.function.arguments),
                }
            else:
                return {
                    "type": "text",
                    "text": choice.message.content,
                }
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}
