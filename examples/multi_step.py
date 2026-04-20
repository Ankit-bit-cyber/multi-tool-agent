"""Multi-turn chained tool use example."""

from src.agent.agent import Agent
from src.llm.client import AnthropicClient
from src.tools.calculator import Calculator
from src.tools.search import SearchTool


def main():
    """Run a multi-turn example with chained tool calls."""
    
    # Initialize LLM client
    llm_client = AnthropicClient()
    
    # Register tools
    tools = {
        "calculator": Calculator.evaluate,
        "search": SearchTool.search,
    }
    
    # Create agent
    agent = Agent(llm_client, tools, max_iterations=15, verbose=True)
    
    # Multi-turn queries
    queries = [
        "Calculate 100 + 200",
        "Now multiply that result by 5",
        "Search for information about climate change",
    ]
    
    for query in queries:
        print(f"\nUser: {query}\n")
        response = agent.run(query)
        print(f"\nAgent: {response}\n")
        print("─" * 60)


if __name__ == "__main__":
    main()
