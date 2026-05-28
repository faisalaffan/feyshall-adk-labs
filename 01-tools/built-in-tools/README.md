---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Built-in Tools

## Concept

ADK ships with pre-built tools for common agent capabilities: Google Search, Code Execution, and Computer Use. These are production-hardened and handle auth/sandboxing automatically.

## Google Search

```python
from google.adk.tools import GoogleSearchTool

agent = Agent(
    name="research-agent",
    model="gemini-2.5-flash",
    tools=[
        GoogleSearchTool(),
    ],
    instruction="Use Google Search to find current information before answering.",
)
```

**Use when:** Agent needs real-time web data, fact-checking, or current events.

## Code Execution

```python
from google.adk.tools import CodeExecutorTool

agent = Agent(
    name="math-agent",
    model="gemini-2.5-flash",
    tools=[
        CodeExecutorTool(
            language="python",
            timeout_seconds=10,
            sandbox=True,  # Isolated execution environment
        ),
    ],
    instruction="Write and execute Python code to solve math problems.",
)
```

**Use when:** Agent needs to compute, transform data, or run code safely.

## Computer Use

```python
from google.adk.tools import ComputerUseTool

agent = Agent(
    name="browser-agent",
    model="gemini-2.5-pro",  # Requires vision-capable model
    tools=[
        ComputerUseTool(
            max_steps=50,
            headless=True,
        ),
    ],
    instruction="Navigate websites to complete user tasks.",
)
```

**Use when:** Agent needs to interact with web UIs, scrape JS-heavy pages, or automate browser workflows.

## Built-in Tool Comparison

| Tool | Latency | Cost | Sandboxed |
|------|---------|------|-----------|
| Google Search | ~500ms | Per-query | N/A |
| Code Executor | ~200ms startup | Per-second | Yes |
| Computer Use | ~2-5s per action | Per-step | No (use with caution) |

## Pitfalls

- **Search quota**: Google Search Tool uses your GCP quota. Rate limit your agent to avoid billing surprises.
- **Code executor timeout**: Default is 30s. Long-running computations need explicit `timeout_seconds`.
- **Computer Use is expensive**: Each "step" (click, scroll, type) costs a full LLM call. A simple login flow can take 10-20 steps.
- **Not available in all regions**: Computer Use requires specific GCP regions. Check availability before building.
