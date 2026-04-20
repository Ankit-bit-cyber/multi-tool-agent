"""CLI entry point for the multi-tool agent."""

import argparse
import sys
from typing import Dict, Any

from src.agent.agent import Agent
from src.llm.client import AnthropicClient, OpenAIClient, LLMClient
from src.tools.calculator import Calculator
from src.tools.weather import WeatherTool
from src.tools.search import SearchTool
from config.settings import load_settings


def create_llm_client(settings) -> LLMClient:
    """Create LLM client based on settings."""
    if settings.llm_provider == "openai":
        return OpenAIClient(model=settings.llm_model)
    else:
        return AnthropicClient(model=settings.llm_model)


def get_enabled_tools(settings) -> Dict[str, Any]:
    """Get enabled tools based on settings."""
    tools = {}
    
    if settings.tools_enabled.get("calculator", True):
        tools["calculator"] = Calculator.evaluate
    
    if settings.tools_enabled.get("weather", True):
        tools["weather"] = WeatherTool.get_weather
    
    if settings.tools_enabled.get("search", True):
        tools["search"] = SearchTool.search
    
    return tools


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Multi-tool AI Agent"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process"
    )
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        help="LLM provider"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    # Load settings
    settings = load_settings()
    
    if args.provider:
        settings.llm_provider = args.provider
    
    if args.verbose:
        settings.verbose = True
    
    # Create LLM client
    llm_client = create_llm_client(settings)
    
    # Get enabled tools
    tools = get_enabled_tools(settings)
    
    # Create agent
    agent = Agent(
        llm_client,
        tools,
        max_iterations=settings.max_iterations,
        verbose=settings.verbose,
    )
    
    if args.interactive:
        # Interactive mode
        print("\n🤖 Multi-tool Agent Interactive Mode")
        print("Type 'exit' or 'quit' to exit\n")
        
        while True:
            try:
                query = input("You: ").strip()
                
                if query.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                
                if not query:
                    continue
                
                response = agent.run(query)
                print(f"\nAgent: {response}\n")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    
    elif args.query:
        # Single query mode
        print(f"\nUser: {args.query}\n")
        response = agent.run(args.query)
        print(f"\nAgent: {response}\n")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
