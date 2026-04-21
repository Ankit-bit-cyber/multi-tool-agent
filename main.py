"""
main.py — CLI entry point for the multi-tool agent.

Usage examples:
  python main.py ask "What is 15% of 847?"
  python main.py ask "What's the weather in Mumbai?" --verbose
  python main.py ask "Who invented Python?" --compare
  python main.py ask "sqrt(144) and weather in Delhi" --verbose --compare
  python main.py tools
  python main.py chat
"""

import sys
import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

# ── ensure project root is on sys.path ───────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from src.tools import build_registry
from src.agent.agent import Agent

app = typer.Typer(
    name="agent",
    help="Multi-tool AI agent powered by Claude.",
    add_completion=False,
)
console = Console()


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_agent(verbose: bool, model: str | None = None) -> Agent:
    registry = build_registry()
    return Agent(registry=registry, verbose=verbose, model=model)


def _print_comparison(query: str, agent_answer: str, direct_answer: str,
                       agent_tokens: int, direct_tokens: int,
                       agent_tools: list[str], agent_ms: float, direct_ms: float) -> None:
    console.print()
    console.print(
        Panel(
            Text(query, style="bold white"),
            title="[bold cyan]Query[/bold cyan]",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    # Side-by-side panels
    agent_panel = Panel(
        Text(agent_answer.strip(), style="white"),
        title="[bold green]🤖 Agent (with tools)[/bold green]",
        subtitle=f"[dim]tools: {', '.join(agent_tools) or 'none'} | {agent_tokens} tokens | {agent_ms:.0f} ms[/dim]",
        border_style="green",
        padding=(0, 2),
        width=80,
    )
    direct_panel = Panel(
        Text(direct_answer.strip(), style="white"),
        title="[bold yellow]💬 Direct LLM (no tools)[/bold yellow]",
        subtitle=f"[dim]{direct_tokens} tokens | {direct_ms:.0f} ms[/dim]",
        border_style="yellow",
        padding=(0, 2),
        width=80,
    )

    console.print(agent_panel)
    console.print(direct_panel)

    # Diff table
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim")
    table.add_column("Metric", style="dim", width=22)
    table.add_column("Agent", justify="right", width=18)
    table.add_column("Direct LLM", justify="right", width=18)
    table.add_row("Tools used", ", ".join(agent_tools) or "none", "—")
    table.add_row("Tokens", str(agent_tokens), str(direct_tokens))
    table.add_row("Latency (ms)", f"{agent_ms:.0f}", f"{direct_ms:.0f}")
    console.print(table)
    console.print()


# ── commands ──────────────────────────────────────────────────────────────────

@app.command()
def ask(
    query: str = typer.Argument(..., help="The question or task for the agent"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show reasoning steps"),
    compare: bool = typer.Option(False, "--compare", "-c", help="Compare agent vs. direct LLM"),
    model: str = typer.Option(None, "--model", "-m", help="Override the LLM model"),
) -> None:
    """Send a single query to the agent and print the answer."""
    agent = _make_agent(verbose=verbose and not compare, model=model)

    if compare:
        # ── agent run ──────────────────────────────────────────────────────
        console.print("\n[dim]Running agent...[/dim]")
        t0 = time.perf_counter()
        agent_result = agent.run(query)
        agent_ms = (time.perf_counter() - t0) * 1000

        # ── direct run ─────────────────────────────────────────────────────
        console.print("[dim]Running direct LLM...[/dim]")
        t1 = time.perf_counter()
        direct_result = agent.run_direct(query)
        direct_ms = (time.perf_counter() - t1) * 1000

        _print_comparison(
            query,
            agent_result.answer,
            direct_result.answer,
            agent_result.total_tokens,
            direct_result.total_tokens,
            agent_result.tool_calls_made,
            agent_ms,
            direct_ms,
        )
    else:
        result = agent.run(query)
        if not verbose:
            console.print()
            console.print(
                Panel(
                    Text(result.answer.strip(), style="white"),
                    title="[bold green]Answer[/bold green]",
                    border_style="green",
                    padding=(0, 2),
                )
            )
            if result.tool_calls_made:
                console.print(
                    f"[dim]  Tools used: {', '.join(result.tool_calls_made)} "
                    f"| {result.total_tokens} tokens[/dim]\n"
                )


@app.command()
def tools() -> None:
    """List all registered tools and their descriptions."""
    registry = build_registry()
    table = Table(
        title="Registered tools",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
    )
    table.add_column("Name", style="bold cyan", width=16)
    table.add_column("Parameters", width=28)
    table.add_column("Description", width=52)

    for schema in registry.anthropic_schemas():
        params = ", ".join(schema["input_schema"]["properties"].keys())
        table.add_row(schema["name"], params, schema["description"][:100])

    console.print()
    console.print(table)
    console.print()


@app.command()
def chat(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show reasoning steps"),
    model: str = typer.Option(None, "--model", "-m", help="Override the LLM model"),
) -> None:
    """Start an interactive chat session with the agent."""
    agent = _make_agent(verbose=verbose, model=model)
    console.print()
    console.print(
        Panel(
            "[bold white]Multi-tool Agent — Interactive Mode[/bold white]\n"
            "[dim]Type your question and press Enter. Type 'exit' or Ctrl-C to quit.[/dim]",
            border_style="cyan",
            padding=(0, 2),
        )
    )

    while True:
        try:
            query = typer.prompt("\n[You]", prompt_suffix=" > ")
        except (typer.Abort, KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if query.strip().lower() in {"exit", "quit", "bye", "q"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        if not query.strip():
            continue

        result = agent.run(query)
        if not verbose:
            console.print(
                Panel(
                    Text(result.answer.strip(), style="white"),
                    title="[bold green]Agent[/bold green]",
                    border_style="green",
                    padding=(0, 2),
                )
            )


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app()