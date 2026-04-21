"""
comparison_demo.py — Side-by-side: Agent (with tools) vs. Direct LLM.

Runs a set of benchmark queries through both modes and prints a
summary table showing where tool use helps and where it doesn't.

Run:
  python examples/comparison_demo.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.tools import build_registry
from src.agent.agent import Agent

console = Console()


BENCHMARK_QUERIES = [
    {
        "query": "What is 17 * 83 + sqrt(256)?",
        "category": "Math",
        "expects_tool": "calculator",
    },
    {
        "query": "What is the current weather in Paris?",
        "category": "Real-time",
        "expects_tool": "weather",
    },
    {
        "query": "What is the speed of light?",
        "category": "Static fact",
        "expects_tool": None,   # LLM should answer directly
    },
    {
        "query": "Search for the latest version of Python.",
        "category": "Current info",
        "expects_tool": "search",
    },
    {
        "query": "If a pizza has 8 slices and costs ₹320, what is the cost per slice?",
        "category": "Math",
        "expects_tool": "calculator",
    },
]


def run_benchmark() -> None:
    registry = build_registry()
    agent = Agent(registry=registry, verbose=False)

    console.print()
    console.print(
        Panel(
            "[bold white]Agent vs. Direct LLM — Benchmark[/bold white]\n"
            "[dim]Each query runs twice: once with tools, once without.[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    results_table = Table(
        title="Benchmark Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold dim",
        min_width=100,
    )
    results_table.add_column("#",        width=3,  style="dim")
    results_table.add_column("Category", width=12)
    results_table.add_column("Query",    width=36)
    results_table.add_column("Tool Used",width=12, style="cyan")
    results_table.add_column("Agent (tok)", width=11, justify="right")
    results_table.add_column("Direct (tok)",width=12, justify="right")
    results_table.add_column("Δ ms",     width=10, justify="right")

    for i, item in enumerate(BENCHMARK_QUERIES, 1):
        query = item["query"]
        cat   = item["category"]

        console.print(f"\n[dim]{i}/{len(BENCHMARK_QUERIES)}[/dim] [white]{query}[/white]")

        # Agent run
        t0 = time.perf_counter()
        agent_result = agent.run(query)
        agent_ms = (time.perf_counter() - t0) * 1000

        console.print(f"  [green]Agent:[/green]  {agent_result.answer[:120]}")

        # Direct run
        t1 = time.perf_counter()
        direct_result = agent.run_direct(query)
        direct_ms = (time.perf_counter() - t1) * 1000

        console.print(f"  [yellow]Direct:[/yellow] {direct_result.answer[:120]}")

        tools_str = ", ".join(agent_result.tool_calls_made) or "[dim]none[/dim]"
        delta_ms  = agent_ms - direct_ms
        delta_str = f"+{delta_ms:.0f}" if delta_ms >= 0 else f"{delta_ms:.0f}"

        results_table.add_row(
            str(i),
            cat,
            query[:35] + ("…" if len(query) > 35 else ""),
            tools_str,
            str(agent_result.total_tokens),
            str(direct_result.total_tokens),
            delta_str,
        )

    console.print()
    console.print(results_table)
    console.print(
        "\n[dim]Δ ms = agent latency minus direct latency. "
        "Positive = agent was slower (expected when tools are called).[/dim]\n"
    )


if __name__ == "__main__":
    run_benchmark()