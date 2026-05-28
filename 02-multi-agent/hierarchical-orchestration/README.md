---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Hierarchical Orchestration

## Concept

A supervisor agent delegates tasks to specialized sub-agents. This is the most scalable multi-agent pattern — the supervisor decides WHO does WHAT, sub-agents just execute.

```
              ┌─► Sub-Agent: Billing ──┐
Supervisor ───┼─► Sub-Agent: Shipping ─┼──► Supervisor (final answer)
              └─► Sub-Agent: Returns  ─┘
```

## Code

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Sub-agents (specialized workers)
billing_agent = Agent(
    name="billing",
    model="gemini-2.5-flash",
    instruction="You handle billing inquiries. Check order totals, payment status, and issue refunds.",
)

shipping_agent = Agent(
    name="shipping",
    model="gemini-2.5-flash",
    instruction="You handle shipping questions. Check tracking numbers, delivery status, and address changes.",
)

returns_agent = Agent(
    name="returns",
    model="gemini-2.5-flash",
    instruction="You handle return requests. Check return eligibility, generate RMA numbers, and explain the return process.",
)

# Delegate function — the key mechanism
def delegate_to_billing(query: str) -> str:
    """Forward a billing-related question to the billing specialist."""
    return run_agent(billing_agent, query)

def delegate_to_shipping(query: str) -> str:
    """Forward a shipping-related question to the shipping specialist."""
    return run_agent(shipping_agent, query)

def delegate_to_returns(query: str) -> str:
    """Forward a return-related question to the returns specialist."""
    return run_agent(returns_agent, query)

# Supervisor agent
supervisor = Agent(
    name="supervisor",
    model="gemini-2.5-pro",  # Needs stronger reasoning for routing
    tools=[
        FunctionTool(delegate_to_billing),
        FunctionTool(delegate_to_shipping),
        FunctionTool(delegate_to_returns),
    ],
    instruction="""You are a customer service supervisor. Route user queries
    to the appropriate specialist. After receiving specialist responses,
    synthesize a final answer for the customer.""",
)
```

## When to Use

- Complex domains where no single agent can know everything
- Customer service with distinct departments
- Enterprise workflows with escalation paths

## Pitfalls

- **Delegation cost**: Each delegation = one LLM call for the supervisor + one for the sub-agent. A complex query can cost 5-10 calls.
- **Supervisor hallucination**: If the supervisor routes incorrectly, the sub-agent gives irrelevant answers. Test routing accuracy.
- **Infinite delegation**: Sub-agents shouldn't delegate back. That creates loops. Enforce a max depth.
- **Context loss**: The supervisor only sees the sub-agent's text output, not the reasoning. If the sub-agent is uncertain, the supervisor won't know.
