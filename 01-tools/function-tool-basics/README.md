---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Function Tool Basics

## Concept

`FunctionTool` is the primary way to give agents capabilities. Any Python function with type hints and a docstring becomes a discoverable tool. The LLM sees the function signature, docstring, and type annotations as the tool description.

## Defining a Tool

```python
from google.adk.tools import FunctionTool
from typing import Optional
from datetime import datetime

def get_weather(city: str, country: Optional[str] = None) -> dict:
    """Get current weather for a city.

    Args:
        city: City name (e.g., "Jakarta").
        country: Optional country code (e.g., "ID").
    """
    # In production, call a real weather API
    return {
        "city": city,
        "temperature_c": 32,
        "humidity": 78,
        "condition": "partly cloudy",
        "recorded_at": datetime.now().isoformat(),
    }
```

## Registering Tools

```python
from google.adk.agents import Agent

agent = Agent(
    name="weather-bot",
    model="gemini-2.5-flash",
    tools=[
        FunctionTool(get_weather),
        FunctionTool(send_email),     # Multiple tools
        FunctionTool(schedule_event),
    ],
)
```

## Type Hints That Matter

| Python Type | LLM Sees | Notes |
|---|---|---|
| `str` | string | Always works |
| `int`, `float` | number | Integer vs float distinction matters |
| `bool` | boolean | Use `strict=True` for exact parsing |
| `list[str]` | array of strings | `list[dict]` works too |
| `Optional[str]` | string, nullable | LLM may skip optional params |
| `Enum` | string enum | LLM respects enum values |
| `datetime` | Use `str` instead | Serialization can be unpredictable |

## Pitfalls

- **Docstrings ARE the tool description**: The LLM never sees your function body. If the docstring is vague, the agent will misuse the tool.
- **Return type matters**: Always annotate the return type. `-> dict` vs `-> str` changes how the LLM uses the result.
- **Complex nested types fail silently**: `dict[str, list[dict[str, Any]]]` may not serialize correctly. Prefer flat dataclasses or TypedDict for complex returns.
- **Mutable defaults**: Don't use `def foo(items: list = [])`. ADK sessions can persist state; mutable defaults cause cross-session contamination.
