"""Rich terminal output formatters."""


def format_step(step_num: int, description: str) -> str:
    """Format a step in the agent loop."""
    return f"\n{'─' * 60}\n📍 Step {step_num}: {description}\n{'─' * 60}"


def format_error(error: str) -> str:
    """Format an error message."""
    return f"❌ Error: {error}"


def format_success(message: str) -> str:
    """Format a success message."""
    return f"✅ Success: {message}"


def format_tool_call(tool_name: str, inputs: dict) -> str:
    """Format a tool call."""
    return f"🔧 Calling {tool_name}({inputs})"


def format_tool_result(result) -> str:
    """Format tool result."""
    return f"→ Result: {result}"


def format_llm_response(response: str) -> str:
    """Format LLM response."""
    return f"🤖 Assistant: {response}"


def format_user_input(user_input: str) -> str:
    """Format user input."""
    return f"👤 User: {user_input}"
