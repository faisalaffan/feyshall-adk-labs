"""First Agent Hello World — Python.
Run: python 00-foundations/first-agent-hello-world/python/main.py
"""
import os
import sys
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! Welcome to ADK."


def main():
    agent = Agent(
        name="hello-world",
        model="gemini-2.5-flash",
        description="A friendly greeting agent",
        instruction="You are a friendly assistant. Use the greet tool when someone tells you their name.",
        tools=[FunctionTool(greet)],
    )

    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService(),
    )

    session = runner.session_service.create_session(
        app_name="hello-world",
        user_id="user-1",
    )

    print("Agent: ", end="", flush=True)
    for event in runner.run(
        user_input="My name is Faisal",
        session=session,
    ):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        sys.exit(1)
    main()
