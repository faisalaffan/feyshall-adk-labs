---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Customer Support Agent

## Concept

The classic AI agent use case, built with production patterns: multi-agent routing, human-in-the-loop for escalations, and audit logging for compliance.

## Architecture

```
User Message
    │
    ▼
Triage Agent (Router)
    │
    ├── "where is my order?" → Shipping Agent
    ├── "I want a refund"    → Billing Agent
    ├── "product question"   → Product Agent
    └── "complaint"          → Escalation Agent → Human
```

## Code

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, AgentTool

# Specialist agents
shipping = Agent(
    name="shipping",
    model="gemini-2.5-flash",
    instruction="Handle shipping inquiries. Look up tracking, explain delays, help with address changes.",
    tools=[FunctionTool(track_order), FunctionTool(update_address)],
)

billing = Agent(
    name="billing",
    model="gemini-2.5-flash",
    instruction="Handle billing issues. Check payments, process refunds, explain charges.",
    tools=[FunctionTool(check_payment), FunctionTool(process_refund)],
)

product = Agent(
    name="product",
    model="gemini-2.5-flash",
    instruction="Answer product questions. Check specs, availability, compatibility.",
    tools=[FunctionTool(search_products), FunctionTool(check_stock)],
)

escalation = Agent(
    name="escalation",
    model="gemini-2.5-flash",
    instruction="Handle complaints. Apologize, summarize the issue, and create a ticket for human review.",
    tools=[FunctionTool(create_support_ticket)],
)

# Triage/router
triage = Agent(
    name="support-triage",
    model="gemini-2.5-flash",
    tools=[
        AgentTool(shipping, description="Route shipping/tracking questions here"),
        AgentTool(billing, description="Route billing/refund questions here"),
        AgentTool(product, description="Route product/stock questions here"),
        AgentTool(escalation, description="Route complaints and angry customers here"),
    ],
    instruction="""Route the customer to the right specialist.
    If the customer is angry (swearing, threatening, mentioning lawyer/refund/chargeback),
    route to escalation immediately. Otherwise, route based on the primary topic.""",
)
```

## Production Checklist

- [ ] Session persistence across browser refreshes
- [ ] Transfer context when routing between agents
- [ ] Queue position for live chat handoff
- [ ] CSAT survey after resolution
- [ ] Audit log for compliance (especially refunds)

## Pitfalls

- **Routing latency**: Triage adds 500ms-2s before the specialist agent responds. For common queries, use rule-based routing (see `dynamic-routing/`).
- **Context gaps**: When triage hands off to billing, the billing agent doesn't see the original message. Pass a structured summary.
- **Escalation timing**: If the agent escalates too early, humans are overwhelmed. If too late, customers are furious. A/B test escalation thresholds.
