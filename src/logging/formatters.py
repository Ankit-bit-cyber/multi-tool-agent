"""
formatters.py — Rich-based terminal formatters for the VerboseLogger.
"""

from __future__ import annotations
import json
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich import box
from rich.console import Group


TOOL_COLORS = {
    "calculator": "yellow",
    "weather": "cyan",
    "search": "green",
    "default": "magenta",
}


def _tool_color(name: str) -> str:
    return TOOL_COLORS.get(name, TOOL_COLORS["default"])


def fmt_step_header(step: int) -> Text:
    t = Text()
    t.append(f"\n  Step {step}", style="bold white")
    t.append("  ─────────────────────────────", style="dim")
    return t


def fmt_llm_thinking(text: str, input_tokens: int, output_tokens: int) -> Panel:
    body = Text(text.strip(), style="italic dim white")
    subtitle = f"[dim]in:{input_tokens} out:{output_tokens} tokens[/dim]"
    return Panel(
        body,
        title="[dim]🧠 LLM reasoning[/dim]",
        subtitle=subtitle,
        border_style="dim",
        padding=(0, 2),
    )


def fmt_tool_call(name: str, args: dict, elapsed_ms: float) -> Panel:
    color = _tool_color(name)
    args_str = json.dumps(args, indent=2, ensure_ascii=False)
    body = Text()
    body.append(f"Tool:   ", style="dim")
    body.append(name, style=f"bold {color}")
    body.append(f"\nArgs:\n{args_str}", style="dim")
    return Panel(
        body,
        title=f"[bold {color}]⚙ Tool call[/bold {color}]",
        subtitle=f"[dim]{elapsed_ms:.0f} ms[/dim]",
        border_style=color,
        padding=(0, 2),
    )


def fmt_tool_result(name: str, result: str) -> Panel:
    color = _tool_color(name)
    truncated = result if len(result) <= 600 else result[:600] + "\n… (truncated)"
    return Panel(
        Text(truncated, style="white"),
        title=f"[{color}]↩ Result from {name}[/{color}]",
        border_style=f"dim {color}",
        padding=(0, 2),
    )


def fmt_final_answer(answer: str) -> Panel:
    return Panel(
        Text(answer.strip(), style="bold white"),
        title="[bold green]✓ Final answer[/bold green]",
        border_style="green",
        padding=(0, 2),
    )


def fmt_summary_table(steps: list, elapsed_ms: float, total_tokens: int) -> Table:
    table = Table(
        title="Run summary",
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
        title_style="bold dim",
        min_width=60,
    )
    table.add_column("Step", style="dim", width=6)
    table.add_column("Action", width=16)
    table.add_column("Tool / Info", width=24)
    table.add_column("Tokens", justify="right", width=10)
    table.add_column("ms", justify="right", width=8)

    for s in steps:
        if s.action == "tool_call":
            color = _tool_color(s.tool_name)
            table.add_row(
                str(s.step),
                f"[{color}]tool call[/{color}]",
                f"[{color}]{s.tool_name}[/{color}]",
                str(s.input_tokens + s.output_tokens),
                f"{s.elapsed_ms:.0f}",
            )
        else:
            table.add_row(
                str(s.step),
                "[green]final answer[/green]",
                "—",
                str(s.input_tokens + s.output_tokens),
                f"{s.elapsed_ms:.0f}",
            )

    table.add_section()
    table.add_row(
        "",
        "[bold]Total[/bold]",
        "",
        f"[bold]{total_tokens}[/bold]",
        f"[bold]{elapsed_ms:.0f}[/bold]",
    )
    return table