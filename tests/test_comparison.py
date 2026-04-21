"""
test_comparison.py — Tests for agent-vs-direct LLM comparison logic.

Run:
  pytest tests/test_comparison.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import build_registry
from src.agent.agent import Agent, AgentResult
from src.llm.client import LLMResponse, ToolCall


def make_tool_response(name, args):
    return LLMResponse(
        content="", tool_calls=[ToolCall(id=f"id_{name}", name=name, arguments=args)],
        input_tokens=40, output_tokens=15, stop_reason="tool_use",
    )

def make_final_response(text):
    return LLMResponse(
        content=text, tool_calls=[],
        input_tokens=60, output_tokens=30, stop_reason="end_turn",
    )


@pytest.fixture
def agent():
    return Agent(registry=build_registry(), verbose=False)


class TestComparison:
    def test_agent_uses_tools_direct_does_not(self, agent):
        agent_responses = [
            make_tool_response("calculator", {"expression": "17 * 83"}),
            make_final_response("17 × 83 = 1411"),
        ]
        direct_response = make_final_response("I think it's around 1411.")

        with patch.object(agent.llm, "chat_with_tools", side_effect=agent_responses):
            agent_result = agent.run("What is 17 * 83?")

        with patch.object(agent.llm, "chat", return_value=direct_response):
            direct_result = agent.run_direct("What is 17 * 83?")

        assert "calculator" in agent_result.tool_calls_made
        assert direct_result.tool_calls_made == []

    def test_agent_result_has_more_tokens_with_tools(self, agent):
        """Agent typically uses more tokens due to tool round-trips."""
        agent_responses = [
            make_tool_response("weather", {"city": "Paris"}),
            make_final_response("It is 18°C in Paris."),
        ]
        direct_response = make_final_response("I don't have live weather data.")

        with patch.object(agent.llm, "chat_with_tools", side_effect=agent_responses):
            agent_result = agent.run("Weather in Paris?")

        with patch.object(agent.llm, "chat", return_value=direct_response):
            direct_result = agent.run_direct("Weather in Paris?")

        # Agent does at least 2 LLM calls, direct does 1
        assert agent_result.total_tokens >= direct_result.total_tokens

    def test_both_return_non_empty_answers(self, agent):
        with patch.object(agent.llm, "chat_with_tools",
                          return_value=make_final_response("42")):
            agent_result = agent.run("Answer?")

        with patch.object(agent.llm, "chat",
                          return_value=make_final_response("42")):
            direct_result = agent.run_direct("Answer?")

        assert agent_result.answer
        assert direct_result.answer

    def test_agent_result_dataclass_fields(self, agent):
        with patch.object(agent.llm, "chat_with_tools",
                          return_value=make_final_response("Done")):
            result = agent.run("Test")
        assert hasattr(result, "answer")
        assert hasattr(result, "steps")
        assert hasattr(result, "total_tokens")
        assert hasattr(result, "tool_calls_made")
        assert hasattr(result, "success")