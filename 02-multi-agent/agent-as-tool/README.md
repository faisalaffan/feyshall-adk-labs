---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Agent as Tool

## Concept

Wrap an entire agent as a tool so another agent can call it. This is simpler than hierarchical orchestration — the calling agent treats the wrapped agent like any other function.

## Code

```python
from google.adk.agents import Agent
from google.adk.tools import AgentTool

# Specialist agent — works independently
translator = Agent(
    name="translator",
    model="gemini-2.5-flash",
    instruction="Translate text to the requested language. Only return the translation, no explanation.",
)

# Main agent — uses translator as a tool
main_agent = Agent(
    name="multilingual-assistant",
    model="gemini-2.5-flash",
    tools=[
        AgentTool(
            agent=translator,
            description="Translate text to another language. Provide source text and target language.",
        ),
    ],
    instruction="You are a multilingual assistant. Use the translator tool when the user needs translation.",
)
```

## AgentTool vs FunctionTool

| | AgentTool | FunctionTool |
|---|---|---|
| **What it wraps** | An entire Agent with LLM | A Python function |
| **Reasoning** | The wrapped agent can reason before responding | Deterministic input → output |
| **Cost** | 1+ LLM calls per invocation | Zero LLM cost |
| **Latency** | 500ms-5s | <10ms |
| **Best for** | Tasks requiring judgment | Deterministic operations |

## Pitfalls

- **Hidden cost**: Calling an agent tool costs at least one full LLM call. A user question that triggers 3 `AgentTool` calls = 4+ LLM invocations.
- **Tool loop risk**: If the calling agent doesn't understand the wrapped agent's output, it may call the tool again. Set `max_turns`.
- **Instruction conflict**: The wrapped agent has its own `instruction`. If it contradicts the caller's intent, the wrapped agent wins. Test edge cases.
