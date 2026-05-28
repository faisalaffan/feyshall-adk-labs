"""Streaming Tool Results — progressive output during long tool execution.
Run: python 04-streaming/streaming-tool-results/main.py
"""
import os
import time
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def search_database(query: str) -> str:
    """Simulate a slow database search with progressive results."""
    results = [
        f"Found: Product A — Rp 25,000\n",
        f"Found: Product B — Rp 48,000\n",
        f"Found: Product C — Rp 12,500\n",
        f"Found: Product D — Rp 89,000\n",
    ]
    output = f"Searching for '{query}'...\n"
    for result in results:
        output += result
        # In production with real streaming: yield each line
    output += f"\nTotal: {len(results)} results for '{query}'."
    return output


def process_batch(data_size: int) -> str:
    """Simulate batch processing with progress milestones."""
    stages = [
        (0, "Loading data..."),
        (0.3, "Cleaning records..."),
        (0.5, "Running analysis..."),
        (0.8, "Generating summary..."),
        (1.0, "Complete."),
    ]
    output = f"Processing {data_size} records:\n"
    for progress, message in stages:
        output += f"  [{progress:.0%}] {message}\n"
    return output


def main():
    print("Streaming Tool Results Demo\n")

    agent = Agent(
        name="search-agent",
        model="gemini-2.5-flash",
        description="Demonstrates streaming tool progress",
        instruction="Use the search_database or process_batch tools when asked. Show the progressive output.",
        tools=[FunctionTool(search_database), FunctionTool(process_batch)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("stream-tools", "user-1")

    for query in ["Search for electronic products", "Process 10000 records"]:
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
