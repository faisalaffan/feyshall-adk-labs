"""Stateful Multi-Turn — runnable example.
Run: python 03-memory-and-state/stateful-multi-turn/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def collect_order(item: str, quantity: int) -> str:
    """Record an item in the order. Returns confirmation."""
    return f"Added {quantity}x {item} to your order."


def finalize_order() -> str:
    """Finalize the current order and show summary."""
    return "Order finalized. Your items have been confirmed."


def main():
    print("Stateful Multi-Turn Demo (Order Taker)\n")

    agent = Agent(
        name="order-agent",
        model="gemini-2.5-flash",
        instruction="""You take food orders. Ask what the customer wants.
        Use collect_order to add items. When they're done, use finalize_order.
        Track what they've ordered using session state.
        Current session state: {session.state}""",
        tools=[FunctionTool(collect_order), FunctionTool(finalize_order)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("order", "customer-1")

    conversation = [
        "I'd like to order 2 nasi goreng and 3 es teh manis",
        "Actually, make it 1 nasi goreng instead",
        "That's all, please finalize",
    ]

    for i, user_msg in enumerate(conversation, 1):
        print(f"--- Turn {i} ---")
        print(f"Customer: {user_msg}")
        print("Agent: ", end="", flush=True)
        for event in runner.run(user_input=user_msg, session=session):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print(f"\nState: {session.state}\n")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
