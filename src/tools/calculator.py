"""
calculator.py — Safe math expression evaluator.

Supports: +  -  *  /  **  %  //  sqrt()  abs()  round()
         sin()  cos()  tan()  log()  log10()  pi  e
"""

import math
import ast
import operator
from src.tools.base import tool

# ── Safe eval ─────────────────────────────────────────────────────────────────

_ALLOWED_NAMES: dict = {
    "abs": abs,
    "round": round,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "floor": math.floor,
    "ceil": math.ceil,
    "pi": math.pi,
    "e": math.e,
    "inf": math.inf,
}

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            val = _ALLOWED_NAMES[node.id]
            if callable(val):
                raise ValueError(f"'{node.id}' needs parentheses: {node.id}(...)")
            return float(val)
        raise ValueError(f"Unknown name: '{node.id}'")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Operator {op_type.__name__} not allowed")
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        return _ALLOWED_OPS[op_type](left, right)
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPS:
            raise ValueError(f"Unary operator {op_type.__name__} not allowed")
        return _ALLOWED_OPS[op_type](_safe_eval(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls allowed")
        func_name = node.func.id
        if func_name not in _ALLOWED_NAMES or not callable(_ALLOWED_NAMES[func_name]):
            raise ValueError(f"Function '{func_name}' not allowed")
        args = [_safe_eval(a) for a in node.args]
        return float(_ALLOWED_NAMES[func_name](*args))
    raise ValueError(f"Unsupported AST node: {type(node).__name__}")


# ── Tool function ─────────────────────────────────────────────────────────────

@tool(
    name="calculator",
    description=(
        "Evaluates a mathematical expression and returns the numeric result. "
        "Supports: +, -, *, /, **, %, //, sqrt(), sin(), cos(), tan(), log(), "
        "log10(), abs(), round(), floor(), ceil(), pi, e. "
        "Do NOT pass code — only pure math expressions like '2 ** 10' or 'sqrt(144)'."
    ),
    param_descriptions={
        "expression": "A mathematical expression string, e.g. '15 % of 847' → '0.15 * 847'"
    },
)
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    # Normalise common natural-language patterns
    import re as _re
    cleaned = expression.strip()
    cleaned = cleaned.replace("^", "**")
    cleaned = cleaned.replace("×", "*")
    cleaned = cleaned.replace("÷", "/")
    cleaned = cleaned.replace(",", "")
    # "15 % of 847"  →  "15 / 100 * 847"
    cleaned = _re.sub(r'%\s+of\b', '/ 100 *', cleaned)
    # "17 % 5" (modulo) must stay as "%"; only bare "%" with no following operand
    # is percent — we DON'T convert plain % so Python's modulo works normally.
    try:
        tree = ast.parse(cleaned, mode="eval")
        result = _safe_eval(tree)
        # Format result: integer if whole number, else 6 sig-fig float
        if result == int(result) and abs(result) < 1e15:
            return str(int(result))
        return f"{result:.6g}"
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as exc:
        return f"Error evaluating expression: {exc}"