# Python Setup

## Prerequisites

- Python 3.10+
- `pip` or `uv`

## Install ADK

```bash
pip install google-adk
```

## Verify

```bash
python -c "import google.adk; print(google.adk.__version__)"
```

## Create Your First Agent

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

agent = Agent(
    name="hello-world",
    model="gemini-2.5-flash",
    description="My first ADK agent",
    tools=[FunctionTool(greet)],
)
```

## Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key"
# Or via LiteLLM for other providers
export OPENAI_API_KEY="your-key"
```
