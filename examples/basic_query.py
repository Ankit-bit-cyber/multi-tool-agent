"""
basic_query.py — Simplest possible agent usage example.

Run:
  python examples/basic_query.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import build_registry
from src.agent.agent import Agent


def main() -> None:
    registry = build_registry()
    agent = Agent(registry=registry, verbose=True)

    queries = [
        "What is 1234 * 5678?",
        "What is the weather in Tokyo?",
        "Who created the Python programming language?",
    ]

    for query in queries:
        print("\n" + "=" * 60)
        result = agent.run(query)
        print(f"\nAnswer: {result.answer}")
        print(f"Tools used: {result.tool_calls_made}")
        print(f"Tokens: {result.total_tokens}")


if __name__ == "__main__":
    main()