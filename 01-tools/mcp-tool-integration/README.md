---
adk_version: "1.28"
level: advanced
languages: [python]
---

# MCP Tool Integration

## Concept

ADK can consume tools from any MCP (Model Context Protocol) server. This means you can connect your agent to hundreds of pre-built MCP servers without writing integration code.

## Architecture

```
ADK Agent
   │
   └── MCPTool(server_command=["npx", "server-name"])
         │
         ├── stdio ──► MCP Server Process
         │                │
         │                ├── Tool: list_files
         │                ├── Tool: search_code
         │                └── Resource: codebase://...
         │
         └── Auto-discovers tools via MCP handshake
```

## Single MCP Server

```python
from google.adk.tools import MCPTool

agent = Agent(
    name="filesystem-agent",
    model="gemini-2.5-flash",
    tools=[
        MCPTool(
            server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
            args=["/path/to/allowed/directory"],
        ),
    ],
    instruction="You can browse and read files in the allowed directory.",
)
```

## Multiple MCP Servers

```python
import os

agent = Agent(
    name="super-agent",
    model="gemini-2.5-flash",
    tools=[
        MCPTool(
            server_command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
            args=["/workspace"],
        ),
        MCPTool(
            server_command=["npx", "-y", "@modelcontextprotocol/server-postgres"],
            env={
                "DATABASE_URL": os.environ["DATABASE_URL"],
            },
        ),
        MCPTool(
            server_command=["npx", "-y", "@modelcontextprotocol/server-github"],
            env={
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ["GITHUB_TOKEN"],
            },
        ),
    ],
    instruction="You have access to filesystem, database, and GitHub tools.",
)
```

## Custom MCP Server (Python)

```python
# mcp_server.py — run with: python mcp_server.py
from mcp.server import Server, stdio_server
from mcp.types import Tool, TextContent

server = Server("my-tools")

@server.tool()
async def get_stock_price(symbol: str) -> list[TextContent]:
    """Get current stock price for a symbol."""
    price = fetch_price(symbol)  # Your implementation
    return [TextContent(type="text", text=f"{symbol}: ${price}")]

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
```

## Pitfalls

- **Process lifecycle**: ADK spawns MCP servers as subprocesses. If the server crashes, tools disappear. Implement health checks.
- **Stdio transport only**: ADK's `MCPTool` currently only supports stdio transport (not HTTP/SSE). Your MCP server must be a local process.
- **Startup latency**: Each MCP server adds 500ms-2s startup time to the first agent run. Cache server connections when possible.
- **Tool name collisions**: If two MCP servers expose a tool with the same name, the last one registered wins. Prefix tool names in custom servers.
