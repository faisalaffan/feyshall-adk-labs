---
adk_version: "1.28"
level: beginner
languages: [python]
---

# Model Configuration

## Concept

ADK supports multiple model providers through a unified configuration interface. You can switch between Gemini, Claude (via LiteLLM), and local models without changing agent logic.

## Gemini (Default)

```python
from google.adk.agents import Agent
from google.adk.models import Gemini

agent = Agent(
    name="gemini-agent",
    model=Gemini(
        model="gemini-2.5-flash",
        temperature=0.2,
        max_output_tokens=4096,
    ),
    description="Agent using Gemini directly",
)
```

## Claude via LiteLLM

```python
from google.adk.agents import Agent
from google.adk.models import LiteLLM

agent = Agent(
    name="claude-agent",
    model=LiteLLM(
        model="claude-sonnet-4-20250514",
        api_key=os.environ["ANTHROPIC_API_KEY"],
        temperature=0.3,
        max_tokens=4096,
    ),
    description="Agent using Claude via LiteLLM proxy",
)
```

## Local Models via Ollama

```python
from google.adk.agents import Agent
from google.adk.models import LiteLLM

agent = Agent(
    name="local-agent",
    model=LiteLLM(
        model="ollama/llama3.2",
        api_base="http://localhost:11434",
        temperature=0.1,
    ),
    description="Agent using local Llama via Ollama",
)
```

## Model Selection Cheatsheet

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| Fast prototyping | `gemini-2.5-flash` | Cheap, fast, good enough |
| Complex reasoning | `gemini-2.5-pro` or `claude-sonnet-4-20250514` | Better tool use, longer context |
| Streaming/audio | `gemini-2.5-flash` | Live API support |
| Offline/air-gapped | `ollama/llama3.2` | Local inference |
| Cost-sensitive prod | `gemini-2.5-flash` | $0.15/M input tokens |

## Pitfalls

- **LiteLLM adds latency**: ~200-500ms overhead vs native SDK. For latency-critical apps, use provider-native agents.
- **Local models lack tool use**: Ollama models often fail at structured tool calling. Test extensively before using in production.
- **API key sprawl**: Each provider needs its own key. Use `env-config-management.md` patterns, never hardcode.
- **Temperature 0 doesn't guarantee determinism**: Gemini and Claude both show variance at temp=0. Use `seed` parameter if available.
