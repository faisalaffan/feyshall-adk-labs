"""Tool Error Handling — runnable example.
Run: python 01-tools/tool-error-handling/main.py
"""
import os
import time
import random
from functools import wraps
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


# --- Retry decorator ---
def with_retries(max_retries: int = 3, backoff: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        wait = backoff * (2**attempt)
                        print(f"  [retry {attempt + 1}/{max_retries} in {wait:.1f}s]")
                        time.sleep(wait)
            raise last_error

        return wrapper

    return decorator


# --- Fallback cache ---
CACHED_WEATHER = {
    "jakarta": {"temp": 32, "condition": "sunny"},
    "bandung": {"temp": 24, "condition": "cloudy"},
}


@with_retries(max_retries=2, backoff=0.5)
def weather_tool(city: str) -> dict:
    """Get weather with automatic retry and fallback.

    Args:
        city: City name.
    """
    # Simulate flaky API (30% failure rate)
    if random.random() < 0.3:
        raise RuntimeError("Weather API timeout")

    city_lower = city.lower()
    if city_lower in CACHED_WEATHER:
        return CACHED_WEATHER[city_lower]

    return {"temp": 30, "condition": "unknown"}


def main():
    random.seed(42)  # Reproducible demo

    agent = Agent(
        name="error-handling-demo",
        model="gemini-2.5-flash",
        description="Demonstrates retry and fallback patterns",
        instruction="Use the weather tool. If it fails, note the retry/fallback behavior.",
        tools=[FunctionTool(weather_tool)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("error-demo", "user-1")

    for query in ["Weather in Jakarta?", "Weather in Bandung?"]:
        print(f"\nUser: {query}")
        print("Agent: ", end="", flush=True)
        try:
            for event in runner.run(user_input=query, session=session):
                if event.content:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
        except RuntimeError as e:
            print(f"[Tool exhausted retries: {e}]")
        print()


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
