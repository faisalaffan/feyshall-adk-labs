---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# AgentOps Integration

## Concept

AgentOps provides session replay for AI agents — you can watch exactly what your agent did, what tools it called, and what the LLM returned. Invaluable for debugging production issues.

## Setup

```bash
pip install agentops
```

```python
import agentops

agentops.init(api_key=os.environ["AGENTOPS_API_KEY"])

# Wrap your ADK agent run
@agentops.record_session
def run_my_agent(user_input: str):
    return run_agent(my_agent, user_input)

# All LLM calls, tool invocations, and responses are now recorded
```

## What You Can Debug

| Issue | How AgentOps Helps |
|-------|-------------------|
| "Agent gave wrong answer" | Replay the full session, see every LLM response |
| "Agent called wrong tool" | See tool selection reasoning in context |
| "Agent looped 10 times" | Visual timeline shows turn-by-turn |
| "Slow response" | Timeline breaks down LLM vs tool latency |
| "Cost spike" | Per-session token and cost breakdown |

## Alternative: Self-Hosted with Langfuse

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
)

trace = langfuse.trace(name="agent-run", session_id=session_id)

for event in runner.run(user_input=query, session=session):
    if event.is_tool_call:
        span = trace.span(name=f"tool:{event.tool_name}")
        span.end(output=event.tool_result)
    elif event.is_final:
        trace.update(output=event.text)
```

## Pitfalls

- **Third-party dependency**: AgentOps and Langfuse are external services. If they're down, your agent should still work — don't block on observability.
- **Data residency**: Session replays may contain PII, API keys in tool args, or proprietary business data. Check where the data is stored.
- **Cost**: AgentOps has a free tier; Langfuse is open-source and self-hostable. Choose based on compliance needs.
