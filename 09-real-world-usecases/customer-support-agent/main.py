"""Customer Support Agent — full runnable example.
Run: python 09-real-world-usecases/customer-support-agent/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent(agent, user_input: str, user_id: str) -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


# --- Tool implementations ---
def track_order(order_id: str) -> dict:
    """Track an order by ID."""
    orders = {
        "12345": {"status": "shipped", "eta": "2 days", "carrier": "JNE"},
        "67890": {"status": "processing", "eta": "5 days"},
    }
    return orders.get(order_id, {"status": "not_found", "message": "Order not found"})


def check_payment(invoice_id: str) -> dict:
    """Check payment status."""
    return {"invoice": invoice_id, "status": "paid", "amount": 500000, "currency": "IDR"}


def process_refund(order_id: str, reason: str) -> dict:
    """Process a refund. Requires approval in production."""
    return {"refund_id": f"REF-{order_id}", "status": "processing", "amount_refunded": 500000}


# --- Specialist agents ---
shipping = Agent(
    name="shipping",
    model="gemini-2.5-flash",
    instruction="Handle shipping/tracking. Use track_order tool.",
    tools=[FunctionTool(track_order)],
)

billing = Agent(
    name="billing",
    model="gemini-2.5-flash",
    instruction="Handle billing/refunds. Use check_payment and process_refund.",
    tools=[FunctionTool(check_payment), FunctionTool(process_refund)],
)


def route_to_shipping(query: str) -> str:
    """Route a shipping question to the shipping agent."""
    return run_agent(shipping, query, "support")


def route_to_billing(query: str) -> str:
    """Route a billing question to the billing agent."""
    return run_agent(billing, query, "support")


def main():
    print("Customer Support Agent Demo\n")

    triage = Agent(
        name="support-triage",
        model="gemini-2.5-flash",
        description="Customer support router",
        instruction="""Route customer questions:
        - Order tracking, shipping, delivery → use route_to_shipping
        - Payments, refunds, invoices → use route_to_billing
        After routing, present the specialist's answer to the customer.""",
        tools=[FunctionTool(route_to_shipping), FunctionTool(route_to_billing)],
    )

    queries = [
        "Where is my order #12345?",
        "I want a refund for my order, the item arrived damaged",
    ]

    for query in queries:
        print(f"Customer: {query}")
        print("Support: ", end="", flush=True)
        for event in Runner(
            agent=triage, session_service=session_service
        ).run(
            user_input=query,
            session=session_service.create_session("triage", "customer-1"),
        ):
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
