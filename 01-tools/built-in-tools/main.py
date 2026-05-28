"""Built-in Tools — runnable example using Google Search.
Requires GOOGLE_API_KEY with Search enabled.
Run: python 01-tools/built-in-tools/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def calculator(expression: str) -> str:
    """Evaluate a simple math expression. Returns the result."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


def main():
    agent = Agent(
        name="tools-demo",
        model="gemini-2.5-flash",
        description="Demonstrates built-in and custom tools",
        instruction="Use the calculator tool for math. Answer other questions directly.",
        tools=[FunctionTool(calculator)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("builtin-demo", "user-1")

    queries = [
        "What is 156 * 34?",
        "What is the capital of Indonesia?",
    ]

    for query in queries:
        print(f"User: {query}")
        print("Agent: ", end="", flush=True)
        for event in runner.run(user_input=query, session=session):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
