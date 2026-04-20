"""System prompts and few-shot examples for LLM."""

SYSTEM_PROMPT = """You are a helpful AI assistant with access to a set of tools.

When you need to use a tool, respond with a tool call in the following format:
<tool_call>
<tool_name>tool_name</tool_name>
<tool_input>{"param1": "value1", "param2": "value2"}</tool_input>
</tool_call>

When you have enough information to answer the user's question, provide a clear and concise response.

Always be helpful, harmless, and honest."""

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "What is 15 + 23?",
    },
    {
        "role": "assistant",
        "content": """I'll calculate that for you.

<tool_call>
<tool_name>calculator</tool_name>
<tool_input>{"expression": "15 + 23"}</tool_input>
</tool_call>""",
    },
    {
        "role": "tool",
        "content": "38",
    },
    {
        "role": "assistant",
        "content": "15 + 23 equals 38.",
    },
]
