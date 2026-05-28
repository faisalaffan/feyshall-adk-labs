---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Unit Testing Agents

## Concept

Testing agents is different from testing regular code. You're testing decisions, not outputs. Mock tools, assert the agent called the right tool with the right arguments, and verify behavior patterns.

## Basic Agent Test

```python
import pytest
from unittest.mock import Mock, patch
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def get_weather(city: str) -> dict:
    """Get weather. In test, this gets mocked."""
    return {"city": city, "temp": 30}

@pytest.fixture
def weather_agent():
    return Agent(
        name="weather",
        model="gemini-2.5-flash",
        tools=[FunctionTool(get_weather)],
    )

def test_agent_calls_weather_tool(weather_agent):
    """Agent should call get_weather when asked about weather."""
    with patch("__main__.get_weather", return_value={"city": "Jakarta", "temp": 32}):
        result = run_agent(weather_agent, "What's the weather in Jakarta?")

    assert "32" in result
    # Verify the tool was actually called
    get_weather.assert_called_once_with(city="Jakarta")
```

## Mocking the LLM (Deterministic Tests)

```python
class MockLLM:
    """Deterministic LLM for testing. No API calls, no flakiness."""

    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0

    def generate(self, prompt: str) -> str:
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

def test_agent_handles_tool_error():
    mock_llm = MockLLM([
        'TOOL_CALL: get_weather(city="Mars")',  # Agent tries tool
        "I couldn't get weather for Mars. Please try a city on Earth.",  # Fallback
    ])

    agent = Agent(
        name="weather",
        model=mock_llm,  # Deterministic — no real LLM
        tools=[FunctionTool(get_weather)],
    )

    result = run_agent(agent, "Weather on Mars?")
    assert "city on Earth" in result.lower()
```

## What to Test

| Test | Priority | Why |
|------|----------|-----|
| Tool is called with correct args | High | Core functionality |
| Agent handles tool errors gracefully | High | Production resilience |
| Agent asks clarifying questions when needed | Medium | UX quality |
| Agent refuses unsafe actions | High | Security |
| Output format matches expected schema | Medium | Downstream consumers |

## Pitfalls

- **Don't test LLM output quality in unit tests**: That's eval, not unit testing. Unit tests verify behavior (which tool was called, error handling).
- **Flaky tests from real LLMs**: Never call a real LLM in unit tests. Mock it or use deterministic test doubles.
- **Over-mocking**: If you mock every dependency, you're testing mocks, not the agent. Strike a balance — mock the LLM and external APIs, but use real tools when possible.
