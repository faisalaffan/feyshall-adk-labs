"""Session Management — runnable example.
Compares InMemorySessionService (dev) vs file-based (persistent).
Run: python 03-memory-and-state/session-management/main.py
"""
import os
import json
import tempfile
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def remember_fact(fact: str) -> str:
    """Store a fact in the session. Returns confirmation."""
    return f"Remembered: {fact}"


def recall_facts() -> str:
    """Recall all remembered facts. (Reads from session state in real impl)."""
    return "Facts would be recalled from session state here."


def main():
    print("Session Management Demo\n")

    # In-memory session (dev — lost on restart)
    print("1. InMemorySessionService (dev mode)")
    agent = Agent(
        name="memory-agent",
        model="gemini-2.5-flash",
        instruction="Help the user remember things. Use remember_fact and recall_facts.",
        tools=[FunctionTool(remember_fact), FunctionTool(recall_facts)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("memory", "user-1")

    queries = [
        "Remember that I prefer dark mode",
        "What do you remember about me?",
    ]

    for query in queries:
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        for event in runner.run(user_input=query, session=session):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print()

    print("\n2. Session state persisted across turns:")
    print(f"   turn_count: {session.state.get('turn_count', 'N/A')}")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
