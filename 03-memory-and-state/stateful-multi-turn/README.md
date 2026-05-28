---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Stateful Multi-Turn

## Concept

Most agent demos are single-turn: one question, one answer. Real applications span 10-50 turns, carrying context, decisions, and partial results across the entire conversation.

## Maintaining State

```python
from google.adk.sessions import Session

class ConversationState:
    """Typed state that persists across turns."""

    def __init__(self, session: Session):
        self.session = session
        if "app_state" not in session.state:
            session.state["app_state"] = {
                "turn_count": 0,
                "user_intent": None,
                "collected_data": {},
                "decisions": [],
                "pending_actions": [],
            }

    @property
    def data(self) -> dict:
        return self.session.state["app_state"]

    def record_turn(self, user_input: str, agent_response: str):
        self.data["turn_count"] += 1
        self.data["decisions"].append({
            "turn": self.data["turn_count"],
            "input": user_input[:200],
            "response": response_summary(agent_response),
        })

    def collect(self, field: str, value):
        """Multi-turn data collection."""
        self.data["collected_data"][field] = value

    def is_complete(self) -> bool:
        """Check if all required fields are collected."""
        required = ["name", "email", "issue_type", "description"]
        return all(f in self.data["collected_data"] for f in required)
```

## Multi-Turn Agent

```python
agent = Agent(
    name="support-agent",
    model="gemini-2.5-flash",
    instruction="""You are a support agent collecting information across multiple turns.
    Use session.state to track what you've already collected.
    Don't ask for information the user already provided.
    Current state: {session.state}""",
)

# Turn 1: "My internet is down"
# → Agent: "I'm sorry to hear that. Can I get your name and account number?"

# Turn 2: "Faisal, ACC-12345"
# → Agent: "Thanks Faisal. What troubleshooting have you tried?"

# Turn 3: "Restarted the router, still nothing"
# → Agent: "I see. Let me check your area for outages..."
```

## Pitfalls

- **State drift**: If the LLM misinterprets state and asks for already-collected info, users get frustrated. Validate state before each turn.
- **Orphaned state**: If a user abandons the conversation and returns later, state may be stale. Add timestamp checks.
- **State as prompt bloat**: Including full `session.state` in every instruction adds tokens. Only include what's relevant to the current turn.
- **No undo**: Users can't "undo" a turn in most implementations. Track a state history stack for rollback.
