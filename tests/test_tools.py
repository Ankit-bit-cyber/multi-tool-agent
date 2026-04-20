"""Unit tests for each tool."""

import pytest
from src.tools.calculator import Calculator
from src.tools.weather import WeatherTool
from src.tools.search import SearchTool


class TestCalculator:
    """Tests for Calculator tool."""
    
    def test_addition(self):
        """Test basic addition."""
        result = Calculator.evaluate("2 + 2")
        assert result == 4
    
    def test_multiplication(self):
        """Test multiplication."""
        result = Calculator.evaluate("3 * 4")
        assert result == 12
    
    def test_complex_expression(self):
        """Test complex expression."""
        result = Calculator.evaluate("(10 + 5) * 2")
        assert result == 30
    
    def test_invalid_expression(self):
        """Test invalid expression handling."""
        result = Calculator.evaluate("invalid")
        assert "Error" in str(result)


class TestWeatherTool:
    """Tests for WeatherTool."""
    
    @pytest.mark.skip(reason="Requires API key")
    def test_get_weather(self):
        """Test weather API call."""
        result = WeatherTool.get_weather("London")
        assert "temperature" in result or "error" in result


class TestSearchTool:
    """Tests for SearchTool."""
    
    @pytest.mark.skip(reason="Requires API key")
    def test_search(self):
        """Test search functionality."""
        result = SearchTool.search("python programming")
        assert isinstance(result, list)
