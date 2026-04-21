"""
logger.py — VerboseLogger: step-by-step trace of the agent reasoning loop.

When verbose=True every iteration prints:
  • What the LLM decided (tool call vs. final answer)
  • Tool name + arguments
  • Tool result
  • Token counts
  • Elapsed time per step
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from src.logging.formatters import (
    fmt_tool_call,
    fmt_tool_result,
    fmt_llm_thinking,
    fmt_final_answer,
    fmt_step_header,
    fmt_summary_table,
)


console = Console()


@dataclass
class StepRecord:
    step: int
    action: str          # "tool_call" | "final_answer" | "direct_answer"
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    tool_result: str = ""
    llm_text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_ms: float = 0.0


class VerboseLogger:
    """
    Logs each agent step to the terminal using Rich formatting.
    When verbose=False, all methods are no-ops.
    """

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.steps: list[StepRecord] = []
        self._step_start: float = 0.0
        self._run_start: float = 0.0

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def run_start(self, query: str) -> None:
        self._run_start = time.perf_counter()
        if not self.verbose:
            return
        console.print()
        console.print(
            Panel(
                Text(query, style="bold white"),
                title="[bold cyan]▶ Agent Query[/bold cyan]",
                border_style="cyan",
                padding=(0, 2),
            )
        )

    def run_end(self, final_answer: str, total_tokens: int) -> None:
        elapsed = (time.perf_counter() - self._run_start) * 1000
        if self.verbose:
            console.print()
            console.print(fmt_final_answer(final_answer))
            console.print(fmt_summary_table(self.steps, elapsed, total_tokens))
            console.print()

    # ── step logging ──────────────────────────────────────────────────────────

    def step_start(self, step: int) -> None:
        self._step_start = time.perf_counter()
        if self.verbose:
            console.print(fmt_step_header(step))

    def llm_thinking(self, text: str, input_tokens: int, output_tokens: int) -> None:
        if self.verbose and text.strip():
            console.print(fmt_llm_thinking(text, input_tokens, output_tokens))

    def tool_call(self, step: int, name: str, args: dict, input_tokens: int, output_tokens: int) -> None:
        elapsed = (time.perf_counter() - self._step_start) * 1000
        record = StepRecord(
            step=step,
            action="tool_call",
            tool_name=name,
            tool_args=args,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            elapsed_ms=elapsed,
        )
        self.steps.append(record)
        if self.verbose:
            console.print(fmt_tool_call(name, args, elapsed))

    def tool_result(self, step: int, name: str, result: str) -> None:
        # Update last record with the result
        for rec in reversed(self.steps):
            if rec.step == step and rec.tool_name == name:
                rec.tool_result = result
                break
        if self.verbose:
            console.print(fmt_tool_result(name, result))

    def final_answer(self, step: int, text: str, input_tokens: int, output_tokens: int) -> None:
        elapsed = (time.perf_counter() - self._step_start) * 1000
        self.steps.append(
            StepRecord(
                step=step,
                action="final_answer",
                llm_text=text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                elapsed_ms=elapsed,
            )
        )

    def error(self, message: str) -> None:
        if self.verbose:
            console.print(f"[bold red]✗ Error:[/bold red] {message}")

    def info(self, message: str) -> None:
        if self.verbose:
            console.print(f"[dim]  {message}[/dim]")

    # ── convenience ───────────────────────────────────────────────────────────

    def total_tokens(self) -> int:
        return sum(s.input_tokens + s.output_tokens for s in self.steps)

    def total_tool_calls(self) -> int:
        return sum(1 for s in self.steps if s.action == "tool_call")