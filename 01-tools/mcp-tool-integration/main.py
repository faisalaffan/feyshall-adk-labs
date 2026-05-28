"""MCP Tool Integration — runnable example.
Requires an MCP server to be running.
Run: python 01-tools/mcp-tool-integration/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import MCPToolset, FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def local_greet(name: str) -> str:
    """Greet someone by name (local function tool)."""
    return f"Hello, {name}! (from local tool)"


def main():
    agent = Agent(
        name="mcp-demo",
        model="gemini-2.5-flash",
        description="Demonstrates MCP tool integration",
        instruction="Use available tools (local and MCP) to help the user.",
        tools=[
            FunctionTool(local_greet),
            # Uncomment and configure to use a real MCP server:
            # MCPToolset(
            #     connection_params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]},
            # ),
        ],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("mcp-demo", "user-1")

    query = "Greet Faisal"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    for event in runner.run(user_input=query, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
