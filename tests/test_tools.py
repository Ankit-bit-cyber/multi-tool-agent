"""
test_tools.py — Unit tests for all three tools.

Run:
  pytest tests/test_tools.py -v
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.calculator import calculator
from src.tools.weather import weather
from src.tools.search import search
from src.tools.base import ToolRegistry, tool, ToolDefinition


# ── Calculator ────────────────────────────────────────────────────────────────

class TestCalculator:
    def test_basic_addition(self):
        assert calculator("2 + 2") == "4"

    def test_multiplication(self):
        assert calculator("12 * 13") == "156"

    def test_power(self):
        assert calculator("2 ** 10") == "1024"

    def test_sqrt(self):
        assert calculator("sqrt(144)") == "12"

    def test_float_result(self):
        result = calculator("1 / 3")
        assert result.startswith("0.333")

    def test_percentage_of(self):
        result = calculator("15 % of 847")
        assert result == "127.05" or float(result) == pytest.approx(127.05, rel=1e-3)

    def test_combined_expression(self):
        result = calculator("2 ** 10 + sqrt(144)")
        assert float(result) == pytest.approx(1036.0)

    def test_pi(self):
        result = calculator("pi")
        assert float(result) == pytest.approx(3.14159, rel=1e-4)

    def test_division_by_zero(self):
        result = calculator("1 / 0")
        assert "zero" in result.lower()

    def test_invalid_expression(self):
        result = calculator("import os")
        assert "Error" in result or "error" in result.lower()

    def test_trig_sin(self):
        result = calculator("sin(0)")
        assert float(result) == pytest.approx(0.0)

    def test_floor_ceil(self):
        assert calculator("floor(3.7)") == "3"
        assert calculator("ceil(3.2)")  == "4"

    def test_caret_power(self):
        assert calculator("3^3") == "27"

    def test_modulo(self):
        assert calculator("17 % 5") == "2"


# ── Weather (demo mode — no API key needed) ───────────────────────────────────

class TestWeather:
    def test_returns_string(self):
        result = weather("Mumbai")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_city_or_demo(self):
        result = weather("London")
        assert "London" in result or "DEMO" in result or "°C" in result

    def test_unknown_city_handled(self):
        # With a real API key this would return "City not found"
        # Without one (demo mode) it returns a mock
        result = weather("xyzzy_nonexistent_city_12345")
        assert isinstance(result, str)

    def test_demo_mode_message(self):
        from unittest.mock import patch
        # Patch the settings object inside the weather module's namespace
        with patch("src.tools.weather.settings") as mock_settings:
            mock_settings.openweather_api_key = ""
            result = weather("Delhi")
        assert isinstance(result, str)
        assert len(result) > 0


# ── Search ────────────────────────────────────────────────────────────────────

class TestSearch:
    def test_returns_string(self):
        result = search("Python programming language")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_result_has_content(self):
        result = search("speed of light")
        # Should have at least a title or snippet
        assert len(result) > 20

    def test_no_exception_on_empty(self):
        result = search("")
        assert isinstance(result, str)


# ── ToolRegistry ──────────────────────────────────────────────────────────────

class TestToolRegistry:
    def setup_method(self):
        self.registry = ToolRegistry()

    def test_register_and_get(self):
        self.registry.register(calculator)
        defn = self.registry.get("calculator")
        assert defn.name == "calculator"

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError):
            self.registry.get("nonexistent")

    def test_register_non_tool_raises(self):
        def plain(): pass
        with pytest.raises(ValueError):
            self.registry.register(plain)

    def test_execute(self):
        self.registry.register(calculator)
        result = self.registry.execute("calculator", expression="6 * 7")
        assert result == "42"

    def test_anthropic_schema_structure(self):
        self.registry.register(calculator)
        schemas = self.registry.anthropic_schemas()
        assert len(schemas) == 1
        s = schemas[0]
        assert "name" in s
        assert "description" in s
        assert "input_schema" in s
        assert s["input_schema"]["type"] == "object"

    def test_openai_schema_structure(self):
        self.registry.register(calculator)
        schemas = self.registry.openai_schemas()
        s = schemas[0]
        assert s["type"] == "function"
        assert "function" in s

    def test_names(self):
        self.registry.register(calculator)
        self.registry.register(weather)
        assert set(self.registry.names()) == {"calculator", "weather"}

    def test_len(self):
        assert len(self.registry) == 0
        self.registry.register(calculator)
        assert len(self.registry) == 1


# ── @tool decorator ───────────────────────────────────────────────────────────

class TestToolDecorator:
    def test_attaches_definition(self):
        @tool(name="test_fn", description="Test function")
        def test_fn(x: int, y: str) -> str:
            return f"{x} {y}"

        assert hasattr(test_fn, "_tool_definition")
        defn: ToolDefinition = test_fn._tool_definition
        assert defn.name == "test_fn"
        assert "x" in defn.parameters
        assert "y" in defn.parameters

    def test_required_params(self):
        @tool(name="req_test", description="Test required params")
        def req_test(a: int, b: str = "default") -> str:
            return ""

        defn: ToolDefinition = req_test._tool_definition
        assert "a" in defn.required
        assert "b" not in defn.required

    def test_function_still_callable(self):
        @tool(name="add", description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        assert add(3, 4) == 7

    def test_param_descriptions(self):
        @tool(
            name="greet",
            description="Greet a person",
            param_descriptions={"name": "Person's name"},
        )
        def greet(name: str) -> str:
            return f"Hello {name}"

        defn: ToolDefinition = greet._tool_definition
        assert defn.parameters["name"]["description"] == "Person's name"