"""Function Tool Basics — runnable example.
Run: python 01-tools/function-tool-basics/main.py
"""
import os
from typing import Optional
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def get_weather(city: str, country: Optional[str] = None) -> dict:
    """Get current weather for a city.

    Args:
        city: City name (e.g., 'Jakarta').
        country: Optional country code (e.g., 'ID').
    """
    return {
        "city": city,
        "country": country or "unknown",
        "temperature_c": 32,
        "humidity": 78,
        "condition": "partly cloudy",
        "recorded_at": datetime.now().isoformat(),
    }


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount between currencies.

    Args:
        amount: The amount to convert.
        from_currency: Source currency code (e.g., 'USD').
        to_currency: Target currency code (e.g., 'IDR').
    """
    rates = {"USD_IDR": 16000, "USD_SGD": 1.35, "SGD_IDR": 11850}
    key = f"{from_currency}_{to_currency}"
    rate = rates.get(key, 1.0)
    return {
        "amount": amount,
        "from": from_currency,
        "to": to_currency,
        "rate": rate,
        "result": round(amount * rate, 2),
    }


def main():
    agent = Agent(
        name="tools-demo",
        model="gemini-2.5-flash",
        description="Demonstrates function tool basics",
        instruction="Use the available tools to answer user questions. Be concise.",
        tools=[FunctionTool(get_weather), FunctionTool(convert_currency)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("tools-demo", "user-1")

    queries = [
        "What's the weather in Jakarta?",
        "Convert 100 USD to IDR",
    ]

    for query in queries:
        print(f"\nUser: {query}")
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
