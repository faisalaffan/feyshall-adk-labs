"""Hierarchical Orchestration — runnable example.
Run: python 02-multi-agent/hierarchical-orchestration/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent(agent, user_input: str, user_id: str = "orchestration") -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


# Sub-agents (specialists)
billing_agent = Agent(
    name="billing",
    model="gemini-2.5-flash",
    instruction="You handle billing: check order totals, payment status, issue refunds. Be concise.",
)

shipping_agent = Agent(
    name="shipping",
    model="gemini-2.5-flash",
    instruction="You handle shipping: tracking numbers, delivery status, address changes. Be concise.",
)

returns_agent = Agent(
    name="returns",
    model="gemini-2.5-flash",
    instruction="You handle returns: check eligibility, generate RMA numbers, explain process. Be concise.",
)


# Delegate functions
def delegate_to_billing(query: str) -> str:
    """Forward billing-related questions to billing specialist."""
    return run_agent(billing_agent, query, "orchestration")


def delegate_to_shipping(query: str) -> str:
    """Forward shipping-related questions to shipping specialist."""
    return run_agent(shipping_agent, query, "orchestration")


def delegate_to_returns(query: str) -> str:
    """Forward return-related questions to returns specialist."""
    return run_agent(returns_agent, query, "orchestration")


def main():
    supervisor = Agent(
        name="supervisor",
        model="gemini-2.5-flash",
        description="Customer service supervisor",
        instruction="""Route queries to the right specialist:
- billing: payments, invoices, refunds
- shipping: tracking, delivery, address
- returns: RMA, return policy, eligibility
After receiving specialist response, give a final answer to the customer.""",
        tools=[
            FunctionTool(delegate_to_billing),
            FunctionTool(delegate_to_shipping),
            FunctionTool(delegate_to_returns),
        ],
    )

    queries = [
        "Where is my package? Tracking number TRK-789.",
        "I want a refund for my last order.",
    ]

    for query in queries:
        print(f"\n{'=' * 50}")
        print(f"Customer: {query}")
        print(f"{'=' * 50}")
        response = run_agent(supervisor, query, "supervisor-session")
        print(f"Final response: {response}")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
