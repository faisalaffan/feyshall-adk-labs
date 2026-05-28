---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Inter-Agent Context Passing

## Concept

When multiple agents work together, they need to share state. ADK offers three patterns: text passing (simple), structured state (recommended), and shared memory (advanced).

## Level 1: Text Passing (Simple)

```python
# Agent A outputs text, Agent B receives it as input
output_a = run_agent(agent_a, user_input)
output_b = run_agent(agent_b, output_a)  # Plain text
```

**Problem**: Agent B must parse format from raw text. Fragile.

## Level 2: Structured State (Recommended)

```python
from dataclasses import dataclass, asdict
from google.adk.sessions import Session

@dataclass
class SharedContext:
    user_intent: str
    extracted_entities: dict
    previous_actions: list[str]
    confidence: float

def agent_a_with_state(query: str, session: Session) -> str:
    """Extract entities and store in session state."""
    result = extract_entities(query)
    context = SharedContext(
        user_intent=result["intent"],
        extracted_entities=result["entities"],
        previous_actions=[],
        confidence=result["confidence"],
    )
    session.state["shared_context"] = asdict(context)
    return f"Extracted: {result['entities']}"

def agent_b_reading_state(query: str, session: Session) -> str:
    """Read shared context from session state."""
    ctx = session.state.get("shared_context", {})
    intent = ctx.get("user_intent", "unknown")
    entities = ctx.get("extracted_entities", {})
    return process_with_context(query, intent, entities)
```

## Level 3: Shared Memory (Advanced)

```python
# For cross-session or persistent shared state, use vector store
from google.adk.memory import VectorMemory

shared_memory = VectorMemory(
    store=QdrantStore(url="http://localhost:6333"),
    embedding_model="text-embedding-004",
)

def agent_with_shared_memory(query: str) -> str:
    # Retrieve what other agents learned from similar queries
    relevant = shared_memory.search(query, top_k=5)
    context = "\n".join(r.content for r in relevant)
    return f"Previous context:\n{context}\n\nUser query: {query}"
```

## When to Use Each Pattern

| Pattern | Best For | Trade-off |
|---------|----------|-----------|
| Text passing | 2-agent chains, simple transforms | Brittle, format-dependent |
| Structured state | 3+ agent workflows, complex data | Requires schema agreement |
| Shared memory | Cross-session, long-term knowledge | Adds vector DB dependency |

## Pitfalls

- **State key collisions**: Multiple agents writing to `session.state` can overwrite each other. Namespace your keys: `agent_a:result`, `agent_b:result`.
- **Stale state**: If Agent A sets state, then the user clarifies their request, Agent B might read the old state. Clear or version state on new user input.
- **Session state isn't serialized cleanly**: Complex objects (dataclasses with nested types) may not survive session serialization. Use JSON-serializable primitives.
