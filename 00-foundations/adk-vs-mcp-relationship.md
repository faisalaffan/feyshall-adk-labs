---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# ADK vs MCP Relationship

## Concept

ADK and MCP (Model Context Protocol) are often confused. **ADK is an agent framework. MCP is a tool/server protocol.** They solve different layers of the stack.

```
User: "What's the weather in Jakarta?"
        │
        ▼
   ┌─────────┐
   │   ADK   │  ← Agent framework (orchestration, state, streaming)
   └────┬────┘
        │ "I need weather data"
        ▼
   ┌─────────┐
   │   MCP   │  ← Tool protocol (discovery, invocation, auth)
   └────┬────┘
        │
        ▼
   ┌─────────────┐
   │ Weather API  │  ← Actual implementation
   └─────────────┘
```

## The Relationship

- **ADK consumes MCP tools**: An ADK agent can use `MCPTool` to connect to any MCP server. The agent doesn't care whether a tool is a local function or a remote MCP endpoint.
- **MCP doesn't know about agents**: An MCP server has no concept of "agent," "session," or "memory." It's stateless tool execution.
- **ADK can BE an MCP server**: You can wrap an ADK agent as an MCP tool, making it callable from other agent frameworks.

## When to Use Each

| Scenario | Use |
|----------|-----|
| "I need an agent that reasons and calls tools" | ADK |
| "I have an API I want AI models to discover" | MCP server |
| "I want my ADK agent to call external APIs via MCP" | ADK + `MCPTool` |
| "I want another framework to call my ADK agent" | Wrap ADK agent as MCP server |

## Code: ADK Agent with MCP Tool

```python
from google.adk.agents import Agent
from google.adk.tools import MCPTool

agent = Agent(
    name="weather-agent",
    model="gemini-2.5-flash",
    tools=[
        MCPTool(
            server_command=["npx", "-y", "@modelcontextprotocol/server-weather"],
            env={"WEATHER_API_KEY": os.environ["WEATHER_API_KEY"]},
        ),
    ],
    description="Agent that checks weather via MCP",
)
```

## Pitfalls

- **MCP server lifecycle**: ADK spawns MCP servers as subprocesses. If the server crashes, the tool becomes unavailable mid-session. Handle `MCPToolError`.
- **Auth duplication**: If both ADK and the MCP server need API keys, you're managing two sets of credentials. Use a shared secret manager.
- **Latency stacking**: LLM → ADK → MCP → external API adds 3-5 network hops. For latency-sensitive tools, use native `FunctionTool` instead.
