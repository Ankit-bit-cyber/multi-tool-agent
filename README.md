# Multi-Tool Agent

A flexible, extensible AI agent framework that orchestrates multiple tools through LLM reasoning. Built with Anthropic Claude and OpenAI GPT support.

## Features

- **Multi-LLM Support**: Works with Anthropic Claude and OpenAI GPT models
- **Tool Orchestration**: Automatic routing and execution of tools based on LLM decisions
- **Extensible Architecture**: Easy to add new tools and capabilities
- **Verbose Logging**: Detailed step-by-step execution traces
- **Memory Management**: Conversation history and tool result tracking
- **Error Handling**: Graceful error management and recovery
- **Configuration Management**: YAML-based tool configuration and settings

## Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │ Query
       ▼
┌─────────────────┐
│  Agent (Main)   │◄─────────┐
├─────────────────┤          │
│ • Router        │          │
│ • Executor      │          │
│ • Memory        │          │
└────────┬────────┘          │
         │                   │
    ┌────▼──────┐            │
    │   LLM     │            │
    │  Client   │            │
    └────┬──────┘            │
         │                   │
    ┌────▼──────────┐        │
    │  Tool Call    │        │
    │  Detection    │        │
    └────┬──────────┘        │
         │                   │
    ┌────▼─────────────┐     │
    │  Tool Execution  │─────┘
    └──────────────────┘
```

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/multi-tool-agent.git
cd multi-tool-agent
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here
SERPAPI_KEY=your_key_here
```

### Tools Configuration

Edit `config/tools_config.yaml` to enable/disable tools and set API preferences:

```yaml
tools:
  calculator:
    enabled: true
  weather:
    enabled: true
  search:
    enabled: true
```

## Usage

### Basic Query

```python
from src.agent.agent import Agent
from src.llm.client import AnthropicClient
from src.tools.calculator import Calculator

llm = AnthropicClient()
tools = {"calculator": Calculator.evaluate}

agent = Agent(llm, tools)
response = agent.run("What is 25 * 4?")
print(response)
```

### CLI Usage

Single query:
```bash
python main.py "What is the weather in London?"
```

Interactive mode:
```bash
python main.py --interactive
```

With specific LLM provider:
```bash
python main.py "Your query" --provider openai --verbose
```

## Available Tools

### Calculator
Evaluates mathematical expressions.

```python
from src.tools.calculator import Calculator
Calculator.evaluate("(100 + 50) * 2")  # Returns: 300
```

### Weather
Fetches current weather data from OpenWeatherMap.

```python
from src.tools.weather import WeatherTool
WeatherTool.get_weather("London", units="metric")
```

### Search
Searches the web using SerpAPI or DuckDuckGo.

```python
from src.tools.search import SearchTool
SearchTool.search("Python programming", num_results=5)
```

## Extending the Agent

### Adding a New Tool

1. Create a new file in `src/tools/`:

```python
from src.tools.base import tool

@tool(
    name="my_tool",
    description="Description of my tool",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"}
        }
    }
)
def my_tool(param1: str) -> str:
    return f"Result: {param1}"
```

2. Register with the agent:

```python
tools = {
    "calculator": Calculator.evaluate,
    "my_tool": my_tool,
}
agent = Agent(llm, tools)
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_tools.py -v
```

With coverage:
```bash
pytest tests/ --cov=src
```

## Project Structure

```
multi-tool-agent/
├── src/
│   ├── agent/          # Core agent orchestration
│   ├── tools/          # Available tools
│   ├── llm/            # LLM client abstractions
│   └── logging/        # Verbose logging
├── tests/              # Test suite
├── config/             # Configuration files
├── examples/           # Example scripts
├── main.py             # CLI entry point
└── README.md          # This file
```

## Examples

See the `examples/` directory for complete examples:

- `basic_query.py`: Simple single-query example
- `multi_step.py`: Multi-turn tool chaining
- `comparison_demo.py`: Agent vs. direct LLM comparison

Run an example:
```bash
python examples/basic_query.py
```

## Performance Considerations

- **Iteration Limit**: Configure `max_iterations` to prevent infinite loops
- **Timeout Handling**: Set appropriate timeouts for API calls
- **Memory Management**: Agent maintains full conversation history

## Troubleshooting

### API Key Issues
- Ensure all required API keys are set in `.env`
- Use `echo $YOUR_KEY` to verify environment variable is set
- Check API key validity and permissions

### Tool Execution Errors
- Check tool input schema matches expected format
- Review verbose output with `--verbose` flag
- Check internet connection for external API tools

### LLM Response Issues
- Verify LLM provider is correctly configured
- Check API rate limits
- Ensure sufficient tokens for response

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [Anthropic Claude](https://www.anthropic.com)
- Supports [OpenAI GPT](https://openai.com)
- Tool framework inspired by LangChain and LlamaIndex

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review example scripts

## Roadmap

- [ ] Async/await support
- [ ] Tool caching
- [ ] Advanced tool composition
- [ ] Memory persistence
- [ ] Web UI dashboard
- [ ] Streaming responses
- [ ] Function calling with more providers
