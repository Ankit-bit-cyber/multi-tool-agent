"""
test_agent.py — Integration tests for the agent loop.

These tests mock the LLM client so no real API calls are made.

Run:
  pytest tests/test_agent.py -v
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import build_registry
from src.agent.agent import Agent, AgentResult
from src.agent.memory import Memory
from src.agent.executor import ToolExecutor
from src.agent.router import ToolRouter
from src.llm.client import LLMResponse, ToolCall


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def registry():
    return build_registry()


@pytest.fixture
def agent(registry):
    return Agent(registry=registry, verbose=False)


def make_tool_response(name: str, args: dict) -> LLMResponse:
    return LLMResponse(
        content="",
        tool_calls=[ToolCall(id=f"call_{name}", name=name, arguments=args)],
        input_tokens=50,
        output_tokens=20,
        stop_reason="tool_use",
    )


def make_final_response(text: str) -> LLMResponse:
    return LLMResponse(
        content=text,
        tool_calls=[],
        input_tokens=80,
        output_tokens=40,
        stop_reason="end_turn",
    )


# ── Router ────────────────────────────────────────────────────────────────────

class TestToolRouter:
    def test_routes_tool_call(self):
        router = ToolRouter()
        resp = make_tool_response("calculator", {"expression": "1+1"})
        assert router.route(resp) == "tool_call"
        assert router.is_tool_call(resp)

    def test_routes_final_answer(self):
        router = ToolRouter()
        resp = make_final_response("The answer is 42.")
        assert router.route(resp) == "final_answer"
        assert router.is_final_answer(resp)


# ── Memory ────────────────────────────────────────────────────────────────────

class TestMemory:
    def test_add_user(self):
        mem = Memory()
        mem.add_user("Hello")
        assert len(mem) == 1
        assert mem.messages[0]["role"] == "user"

    def test_add_assistant_text(self):
        mem = Memory()
        mem.add_assistant_text("Hi there")
        assert mem.messages[0]["role"] == "assistant"

    def test_add_tool_results(self):
        mem = Memory()
        tc = ToolCall(id="call_1", name="calculator", arguments={"expression": "1+1"})
        mem.add_tool_results([tc], ["2"])
        msg = mem.messages[0]
        assert msg["role"] == "user"
        assert msg["content"][0]["type"] == "tool_result"
        assert msg["content"][0]["content"] == "2"

    def test_snapshot_is_copy(self):
        mem = Memory()
        mem.add_user("test")
        snap = mem.snapshot()
        snap.append({"role": "user", "content": "extra"})
        assert len(mem.messages) == 1   # original unaffected

    def test_clear(self):
        mem = Memory()
        mem.add_user("test")
        mem.clear()
        assert len(mem) == 0


# ── Executor ──────────────────────────────────────────────────────────────────

class TestToolExecutor:
    def test_execute_calculator(self, registry):
        executor = ToolExecutor(registry)
        tc = ToolCall(id="c1", name="calculator", arguments={"expression": "6 * 7"})
        result = executor.run(tc)
        assert result == "42"

    def test_unknown_tool_returns_error(self, registry):
        executor = ToolExecutor(registry)
        tc = ToolCall(id="c2", name="nonexistent", arguments={})
        result = executor.run(tc)
        assert "not registered" in result

    def test_bad_args_returns_error(self, registry):
        executor = ToolExecutor(registry)
        tc = ToolCall(id="c3", name="calculator", arguments={"wrong_param": "x"})
        result = executor.run(tc)
        assert "Error" in result

    def test_run_all(self, registry):
        executor = ToolExecutor(registry)
        tcs = [
            ToolCall(id="c4", name="calculator", arguments={"expression": "2+2"}),
            ToolCall(id="c5", name="calculator", arguments={"expression": "3*3"}),
        ]
        results = executor.run_all(tcs)
        assert results == ["4", "9"]


# ── Agent (mocked LLM) ────────────────────────────────────────────────────────

class TestAgent:
    def test_direct_answer_no_tools(self, agent):
        """LLM answers directly without calling any tools."""
        with patch.object(agent.llm, "chat_with_tools",
                          return_value=make_final_response("The answer is 42.")):
            result = agent.run("What is the meaning of life?")
        assert result.answer == "The answer is 42."
        assert result.tool_calls_made == []

    def test_single_tool_call(self, agent):
        """LLM calls calculator once, then gives a final answer."""
        responses = [
            make_tool_response("calculator", {"expression": "6 * 7"}),
            make_final_response("6 × 7 = 42."),
        ]
        with patch.object(agent.llm, "chat_with_tools", side_effect=responses):
            result = agent.run("What is 6 times 7?")
        assert "42" in result.answer
        assert "calculator" in result.tool_calls_made

    def test_multi_tool_chain(self, agent):
        """LLM calls two tools in sequence."""
        responses = [
            make_tool_response("calculator", {"expression": "100 * 0.15"}),
            make_tool_response("weather",    {"city": "Delhi"}),
            make_final_response("15% of 100 is 15. Weather in Delhi is warm."),
        ]
        with patch.object(agent.llm, "chat_with_tools", side_effect=responses):
            result = agent.run("What is 15% of 100 and what's the weather in Delhi?")
        assert "calculator" in result.tool_calls_made
        assert "weather"    in result.tool_calls_made

    def test_max_iterations_respected(self, agent):
        """Agent stops after max_iterations and requests a final summary."""
        agent.max_iterations = 2
        always_tool = make_tool_response("calculator", {"expression": "1+1"})
        final = make_final_response("I've done what I can.")
        with patch.object(agent.llm, "chat_with_tools",
                          return_value=always_tool):
            with patch.object(agent.llm, "chat", return_value=final):
                result = agent.run("Loop forever")
        assert isinstance(result.answer, str)

    def test_run_direct_no_tools(self, agent):
        """run_direct sends no tools to the LLM."""
        direct_resp = make_final_response("Light travels at 3×10⁸ m/s.")
        with patch.object(agent.llm, "chat", return_value=direct_resp):
            result = agent.run_direct("What is the speed of light?")
        assert result.tool_calls_made == []
        assert "3" in result.answer

    def test_agent_result_fields(self, agent):
        """AgentResult contains expected metadata."""
        with patch.object(agent.llm, "chat_with_tools",
                          return_value=make_final_response("Done.")):
            result = agent.run("Hello")
        assert isinstance(result.steps, int)
        assert isinstance(result.total_tokens, int)
        assert result.success is True