"""Side-by-side agent vs. direct LLM comparison."""

from src.llm.client import AnthropicClient
from src.agent.agent import Agent
from src.tools.calculator import Calculator


def compare_agent_vs_direct_llm():
    """Compare agent with tool use vs. direct LLM."""
    
    llm_client = AnthropicClient()
    
    test_queries = [
        "What is 15 * 23?",
        "Calculate (100 + 50) / 5",
        "What is the square root of 144?",
    ]
    
    print("=" * 60)
    print("AGENT vs. DIRECT LLM COMPARISON")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        print("-" * 60)
        
        # Direct LLM approach
        print("\n🤖 Direct LLM Response:")
        direct_response = llm_client.complete(
            messages=[{"role": "user", "content": query}]
        )
        print(direct_response.get("text", direct_response.get("error")))
        
        # Agent approach
        print("\n🔧 Agent with Tools Response:")
        agent = Agent(
            llm_client,
            {"calculator": Calculator.evaluate},
            verbose=False
        )
        agent_response = agent.run(query)
        print(agent_response)
        
        print("-" * 60)


if __name__ == "__main__":
    compare_agent_vs_direct_llm()
