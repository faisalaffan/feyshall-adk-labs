"""Async Tools — runnable example.
Run: python 01-tools/async-tools/main.py
"""
import os
import asyncio
import time
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


async def fetch_product_price(sku: str) -> dict:
    """Fetch current price for a product SKU.

    Args:
        sku: Product SKU code.
    """
    await asyncio.sleep(0.5)  # Simulates network I/O
    return {"sku": sku, "price": 249000, "currency": "IDR"}


async def check_inventory(sku: str) -> dict:
    """Check warehouse inventory for a SKU.

    Args:
        sku: Product SKU code.
    """
    await asyncio.sleep(0.3)
    return {"sku": sku, "stock": 42, "warehouse": "Jakarta Pusat"}


def main():
    print("Async Tools Demo")
    print("Both tools run concurrently when called in the same LLM turn.\n")

    agent = Agent(
        name="inventory-agent",
        model="gemini-2.5-flash",
        description="Async inventory tools demo",
        instruction="Use the tools to check product price and inventory.",
        tools=[FunctionTool(fetch_product_price), FunctionTool(check_inventory)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("async-demo", "user-1")

    query = "Check price and stock for SKU-123"
    print(f"User: {query}")

    start = time.monotonic()
    print("Agent: ", end="", flush=True)
    for event in runner.run(user_input=query, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    elapsed = time.monotonic() - start
    print(f"\n\nTotal time: {elapsed:.1f}s (async tools run concurrently)")
    print("Sync would take: ~0.8s (0.5s + 0.3s), async: ~0.5s (max of both)")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
