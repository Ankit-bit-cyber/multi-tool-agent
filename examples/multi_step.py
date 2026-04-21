"""
multi_step.py — Demonstrates multi-tool chaining in a single query.

The agent will call multiple tools in sequence to answer compound questions.

Run:
  python examples/multi_step.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import build_registry
from src.agent.agent import Agent


MULTI_STEP_QUERIES = [
    # Requires: calculator
    "If I invest ₹50,000 at 8% annual interest for 5 years compounded annually, "
    "what will my final amount be? Show the formula.",

    # Requires: weather + calculator
    "What is the current temperature in London in Fahrenheit? "
    "(Hint: F = C × 9/5 + 32)",

    # Requires: search + calculator
    "Search for the population of India and divide it by the population of Mumbai "
    "to find approximately how many Mumbais fit into India.",
]


def main() -> None:
    registry = build_registry()
    agent = Agent(registry=registry, verbose=True)

    for i, query in enumerate(MULTI_STEP_QUERIES, 1):
        print(f"\n{'═' * 70}")
        print(f"  Multi-step query {i}/{len(MULTI_STEP_QUERIES)}")
        print(f"{'═' * 70}")

        result = agent.run(query)

        print(f"\n✓ Answer: {result.answer}")
        print(f"  Steps: {result.steps} | Tools: {result.tool_calls_made} | Tokens: {result.total_tokens}")


if __name__ == "__main__":
    main()