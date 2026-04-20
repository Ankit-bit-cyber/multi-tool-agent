"""Simple one-shot agent example."""

from src.agent.agent import Agent
from src.llm.client import AnthropicClient
from src.tools.calculator import Calculator
from src.tools.weather import WeatherTool
from src.tools.search import SearchTool


def main():
    """Run a simple one-shot agent example."""
    
    # Initialize LLM client
    llm_client = AnthropicClient()
    
    # Register tools
    tools = {
        "calculator": Calculator.evaluate,
        "weather": WeatherTool.get_weather,
        "search": SearchTool.search,
    }
    
    # Create agent
    agent = Agent(llm_client, tools, verbose=True)
    
    # Run query
    query = "What is 25 * 4?"
    print(f"\nUser: {query}\n")
    
    response = agent.run(query)
    print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()
