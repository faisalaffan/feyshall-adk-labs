---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Testing Sub-Agents

## Concept

ADK doesn't natively support testing sub-agents in isolation. When a supervisor delegates to a sub-agent, testing that interaction requires workarounds.

## The Problem

```python
# You can't easily mock this in ADK's current test framework
supervisor = Agent(
    name="supervisor",
    tools=[AgentTool(sub_agent)],  # Sub-agent is embedded
)
```

## Workaround: Dependency Injection

```python
class AgentFactory:
    """Injectable factory for creating sub-agents. Swap in tests."""

    def create_billing_agent(self):
        return Agent(
            name="billing",
            model="gemini-2.5-flash",
            instruction="Handle billing inquiries.",
        )

    def create_shipping_agent(self):
        return Agent(
            name="shipping",
            model="gemini-2.5-flash",
            instruction="Handle shipping questions.",
        )

def create_supervisor(factory: AgentFactory = None):
    if factory is None:
        factory = AgentFactory()

    return Agent(
        name="supervisor",
        model="gemini-2.5-flash",
        tools=[
            AgentTool(factory.create_billing_agent()),
            AgentTool(factory.create_shipping_agent()),
        ],
    )
```

## Testing with Mock Sub-Agents

```python
class MockAgentFactory(AgentFactory):
    """Returns mock sub-agents for deterministic testing."""

    def create_billing_agent(self):
        return MockAgent(
            name="billing",
            responses=["Invoice #123 is paid. Amount: $500."],
        )

    def create_shipping_agent(self):
        return MockAgent(
            name="shipping",
            responses=["Package shipped. Tracking: TRK-789."],
        )

def test_supervisor_routes_to_correct_sub_agent():
    factory = MockAgentFactory()
    supervisor = create_supervisor(factory)

    result = run_agent(supervisor, "Where is my package?")

    assert "TRK-789" in result
    assert factory.billing_called == False  # Shouldn't call billing
    assert factory.shipping_called == True
```

## Testing Strategy

```
Level 1: Unit test each sub-agent independently (mock tools)
Level 2: Test supervisor routing logic (mock sub-agents)
Level 3: Integration test full chain (real sub-agents, mock LLM)
Level 4: E2E test (real everything, sampled periodically)
```

## Pitfalls

- **This is a known weak spot**: ADK's test isolation for sub-agents is limited. The patterns above are workarounds — expect them to change as ADK matures.
- **Factory pattern overhead**: The dependency injection adds boilerplate. For small projects, skip it and test at the integration level.
- **Mock agent fidelity**: A mock sub-agent that always returns the same string won't catch edge cases. Use more sophisticated mocks that simulate real behavior.
