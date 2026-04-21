"""
agent.py — Main Agent class.

Orchestration loop:
  1. Add user query to memory
  2. Call LLM with tool schemas
  3. If tool_call → execute tools → add results → go to 2
  4. If final_answer → return to caller
  5. If max_iterations reached → return partial answer with warning
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.llm.client import LLMClient, LLMResponse
from src.llm.prompts import AGENT_SYSTEM_PROMPT
from src.tools.base import ToolRegistry
from src.agent.memory import Memory
from src.agent.executor import ToolExecutor
from src.agent.router import ToolRouter
from src.logging.logger import VerboseLogger
from config.settings import settings


@dataclass
class AgentResult:
    answer: str
    steps: int
    total_tokens: int
    tool_calls_made: list[str] = field(default_factory=list)
    success: bool = True
    error: str = ""


class Agent:
    """
    A ReAct-style agent that loops until the LLM produces a final
    text answer or the iteration limit is reached.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        verbose: bool | None = None,
        max_iterations: int | None = None,
        model: str | None = None,
    ) -> None:
        self.registry = registry
        self.verbose = verbose if verbose is not None else settings.verbose
        self.max_iterations = max_iterations or settings.max_iterations

        self.llm = LLMClient(model=model)
        self.executor = ToolExecutor(registry)
        self.router = ToolRouter()
        self.logger = VerboseLogger(verbose=self.verbose)

    # ── public API ────────────────────────────────────────────────────────────

    def run(self, query: str) -> AgentResult:
        """
        Run the agent on a single query.
        Returns an AgentResult with the final answer and metadata.
        """
        memory = Memory()
        memory.add_user(query)

        self.logger.run_start(query)

        tool_schemas = self.registry.anthropic_schemas()
        tools_called: list[str] = []
        total_tokens = 0
        final_answer = ""

        for step in range(1, self.max_iterations + 1):
            self.logger.step_start(step)

            # ── LLM call ──────────────────────────────────────────────────────
            response: LLMResponse = self.llm.chat_with_tools(
                messages=memory.snapshot(),
                tools=tool_schemas,
                system=AGENT_SYSTEM_PROMPT,
            )
            total_tokens += response.input_tokens + response.output_tokens

            # Log any reasoning text the LLM produced alongside its decision
            if response.content:
                self.logger.llm_thinking(
                    response.content,
                    response.input_tokens,
                    response.output_tokens,
                )

            # ── Route ─────────────────────────────────────────────────────────
            if self.router.is_final_answer(response):
                final_answer = response.content
                self.logger.final_answer(
                    step, final_answer,
                    response.input_tokens,
                    response.output_tokens,
                )
                break

            # ── Tool calls ────────────────────────────────────────────────────
            for tc in response.tool_calls:
                self.logger.tool_call(
                    step, tc.name, tc.arguments,
                    response.input_tokens,
                    response.output_tokens,
                )
                tools_called.append(tc.name)

            # Execute all tool calls in this turn
            results = self.executor.run_all(response.tool_calls)

            for tc, result in zip(response.tool_calls, results):
                self.logger.tool_result(step, tc.name, result)

            # Update memory: assistant tool_use turn + tool_result turn
            memory.add_assistant_tool_calls(response.tool_calls, response.content)
            memory.add_tool_results(response.tool_calls, results)

        else:
            # Iteration limit hit — ask for a summary with what we have
            self.logger.error(
                f"Reached max iterations ({self.max_iterations}). "
                "Requesting final summary from LLM."
            )
            memory.add_user(
                "You have reached the maximum number of steps. "
                "Please summarise what you have found so far and give the best answer you can."
            )
            response = self.llm.chat(
                messages=memory.snapshot(),
                system=AGENT_SYSTEM_PROMPT,
            )
            final_answer = response.content
            total_tokens += response.input_tokens + response.output_tokens

        self.logger.run_end(final_answer, total_tokens)

        return AgentResult(
            answer=final_answer,
            steps=len(self.logger.steps),
            total_tokens=total_tokens,
            tool_calls_made=tools_called,
            success=bool(final_answer),
        )

    # ── direct LLM (no tools) — used for comparison ──────────────────────────

    def run_direct(self, query: str) -> AgentResult:
        """
        Send the query directly to the LLM with no tools attached.
        Used for the side-by-side comparison mode.
        """
        from src.llm.prompts import DIRECT_LLM_SYSTEM_PROMPT

        response = self.llm.chat(
            messages=[LLMClient.user_message(query)],
            system=DIRECT_LLM_SYSTEM_PROMPT,
        )
        return AgentResult(
            answer=response.content,
            steps=1,
            total_tokens=response.input_tokens + response.output_tokens,
            tool_calls_made=[],
        )