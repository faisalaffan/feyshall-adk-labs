---
adk_version: "1.28"
level: beginner
languages: [python]
---

# First Agent — Hello World (Python)

## Concept

The simplest possible ADK agent: one tool, one model, one response. This is the starting point for every recipe in this cookbook.

## Prerequisites

```bash
pip install google-adk
export GOOGLE_API_KEY="your-api-key"
```

## Code

```python
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# 1. Define a tool — any Python function with type hints
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to ADK."

# 2. Create the agent
agent = Agent(
    name="hello-world",
    model="gemini-2.5-flash",
    description="A friendly greeting agent",
    instruction="You are a friendly assistant. Use the greet tool when someone tells you their name.",
    tools=[FunctionTool(greet)],
)

# 3. Create a runner and session
runner = Runner(
    agent=agent,
    session_service=InMemorySessionService(),
)

# 4. Run the agent
session = runner.session_service.create_session(
    app_name="hello-world",
    user_id="user-1",
)

for event in runner.run(
    user_input="My name is Faisal",
    session=session,
):
    if event.content:
        for part in event.content.parts:
            if part.text:
                print(part.text, end="", flush=True)
```

## Expected Output

```
Hello, Faisal! Welcome to ADK.
```

## Structure

```
first-agent-hello-world/python/
├── main.py       ← the agent code above
├── requirements.txt
└── README.md     ← you are here
```

## Pitfalls

- **API key must be exported**, not hardcoded. The SDK reads `GOOGLE_API_KEY` from the environment.
- **Session is required** even for single-turn interactions. `InMemorySessionService` is fine for dev; use `redis-session-backend/` for production.
- **`runner.run()` returns a generator**. Nothing executes until you iterate over it. This enables streaming — see `04-streaming/`.
