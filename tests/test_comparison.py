"""Agent vs. direct LLM evaluation tests."""

import pytest


class TestComparison:
    """Comparison tests between agent and direct LLM."""
    
    @pytest.mark.skip(reason="Requires LLM client")
    def test_agent_vs_direct_llm(self):
        """Compare agent tool use vs. direct LLM for same query."""
        pass
    
    @pytest.mark.skip(reason="Requires LLM client")
    def test_agent_accuracy(self):
        """Test accuracy of agent responses."""
        pass
