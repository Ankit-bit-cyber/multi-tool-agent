"""LLM module for client abstractions and prompts."""

from .client import LLMClient, AnthropicClient, OpenAIClient
from .prompts import SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

__all__ = ["LLMClient", "AnthropicClient", "OpenAIClient", "SYSTEM_PROMPT", "FEW_SHOT_EXAMPLES"]
