"""Integration tests for the agent loop."""

import pytest
from src.agent.agent import Agent
from src.agent.memory import ConversationMemory
from src.agent.router import Router
from src.agent.executor import Executor


class TestConversationMemory:
    """Tests for ConversationMemory."""
    
    def test_add_user_message(self):
        """Test adding user message."""
        memory = ConversationMemory()
        memory.add_user_message("Hello")
        assert len(memory.messages) == 1
        assert memory.messages[0]["role"] == "user"
    
    def test_add_tool_result(self):
        """Test adding tool result."""
        memory = ConversationMemory()
        memory.add_tool_result("calculator", 42)
        assert len(memory.messages) == 1
        assert memory.messages[0]["role"] == "tool"
    
    def test_reset(self):
        """Test memory reset."""
        memory = ConversationMemory()
        memory.add_user_message("Hello")
        memory.reset()
        assert len(memory.messages) == 0


class TestExecutor:
    """Tests for Executor."""
    
    def test_execute_registered_tool(self):
        """Test executing a registered tool."""
        from src.tools.calculator import Calculator
        
        tools = {"calculator": Calculator.evaluate}
        executor = Executor(tools)
        
        result = executor.execute("calculator", expression="2 + 2")
        assert result == 4
    
    def test_execute_unregistered_tool(self):
        """Test executing unregistered tool raises error."""
        executor = Executor({})
        
        with pytest.raises(ValueError):
            executor.execute("nonexistent")


class TestAgent:
    """Tests for Agent."""
    
    @pytest.mark.skip(reason="Requires LLM client")
    def test_agent_initialization(self):
        """Test agent initialization."""
        from src.llm.client import AnthropicClient
        from src.tools.calculator import Calculator
        
        llm_client = AnthropicClient()
        tools = {"calculator": Calculator.evaluate}
        
        agent = Agent(llm_client, tools)
        assert agent.max_iterations == 10
