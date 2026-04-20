"""Calculator tool — math expression evaluator."""

import re
from typing import Union
from .base import tool


class Calculator:
    """Math expression evaluator tool."""
    
    @staticmethod
    @tool(
        name="calculator",
        description="Evaluate mathematical expressions and return the result",
        input_schema={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        }
    )
    def evaluate(expression: str) -> Union[float, str]:
        """
        Evaluate a mathematical expression safely.
        
        Args:
            expression: Math expression (e.g., "2 + 2 * 3")
            
        Returns:
            Evaluation result
        """
        try:
            # Sanitize input
            if not Calculator._is_safe_expression(expression):
                return "Error: Invalid expression"
            
            result = eval(expression, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def _is_safe_expression(expression: str) -> bool:
        """Check if expression is safe to evaluate."""
        # Only allow numbers, operators, and basic math functions
        allowed = re.compile(r"^[\d\s+\-*/().,]+$")
        return bool(allowed.match(expression))
