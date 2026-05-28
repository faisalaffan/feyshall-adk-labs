---
adk_version: "1.28"
level: beginner
languages: [python]
---

# Local Dev Setup

## Concept

ADK provides a built-in dev UI and CLI for rapid iteration. No external tools needed — one command starts a web UI where you can chat with your agent.

## CLI Quickstart

```bash
pip install google-adk
export GOOGLE_API_KEY="your-key"

# Start the dev UI
adk web

# Or run a one-shot command
adk run "What's the weather in Jakarta?"
```

## Dev UI Features

```
┌─────────────────────────────────────────┐
│  ADK Dev UI          [Session: abc123]  │
├─────────────────────────────────────────┤
│                                         │
│  🤖 Agent: Hello! How can I help?      │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  [Type your message...]          [Send] │
│                                         │
├─────────────────────────────────────────┤
│  📊 Session State    🔧 Tools           │
│  ├── turn_count: 3   ├── get_weather   │
│  └── user_name: null └── send_email    │
└─────────────────────────────────────────┘
```

## Hot Reload

```python
# agent.py — save this, dev UI picks up changes automatically
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

def get_time() -> str:
    """Get current server time."""
    return datetime.now().isoformat()

agent = Agent(
    name="dev-agent",
    model="gemini-2.5-flash",
    tools=[FunctionTool(get_time)],
)
```

```bash
adk web --agent agent.py --hot-reload
# Edit agent.py → save → changes reflected immediately
```

## Project Structure for Dev

```
my-agent/
├── agent.py          # Agent definition
├── tools.py          # Tool implementations
├── instructions.txt  # System prompt (optional)
└── .env              # GOOGLE_API_KEY=... (never commit)
```

## Pitfalls

- **Dev UI is not for production**: No auth, rate limiting, or persistent sessions. It's a development tool.
- **API key exposure**: The dev UI runs locally, but if you expose it on a network, your API key is visible. Always use `.env` with `.gitignore`.
- **Hot reload limitations**: Adding new dependencies (new `import`) requires restart. Only code changes within already-imported modules hot-reload.
