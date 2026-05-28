---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Context Compaction

## Concept

Every agent turn appends to conversation history. After 20+ turns, you exceed context windows or pay for tokens you don't need. Context compaction summarizes old messages so the agent stays fast and cheap.

## The Problem

```
Turn 1: 100 tokens
Turn 2: 200 tokens
Turn 3: 350 tokens
...
Turn 30: 15,000 tokens → Beyond flash's 8K context? Costs 15x more than turn 1.
```

## Summarization Strategy

```python
class ContextCompactor:
    def __init__(self, summary_model="gemini-2.5-flash-lite"):
        self.summary_model = summary_model
        self.compact_threshold = 5000  # Tokens before compaction

    def maybe_compact(self, session_history: list, current_tokens: int) -> list:
        if current_tokens < self.compact_threshold:
            return session_history

        # Split: recent messages stay verbatim, older ones get summarized
        recent = session_history[-5:]   # Last 5 turns stay as-is
        older = session_history[:-5]    # Everything else gets summarized

        summary = self._summarize(older)
        return [{"role": "system", "content": f"Previous conversation summary: {summary}"}] + recent

    def _summarize(self, messages: list) -> str:
        text = "\n".join(m["content"] for m in messages if "content" in m)
        # In production: call a fast/small model for summarization
        return f"Prior conversation ({len(messages)} messages): user discussed topics including... "
```

## Token Budgeting

```python
TOKEN_BUDGET = {
    "system_prompt": 500,
    "tools_definitions": 1000,
    "memory_context": 500,
    "conversation_history": 4000,   # Compact if exceeds
    "user_input": 1000,
    "output_reserved": 2000,
    "total_window": 9000,           # Matches gemini-2.5-flash context
}
```

## Compaction Triggers

| Trigger | Action |
|---------|--------|
| Conversation > 20 turns | Summarize turns 1-15 |
| Token count > 80% of window | Aggressive compaction |
| Session > 1 hour old | Summarize + add timestamp |
| User explicitly asks "forget" | Drop all but system + last turn |

## Pitfalls

- **Over-summarization loses detail**: If a user referenced "that thing from earlier," a summary may not contain it. Keep entity mentions in summaries.
- **Compaction cost**: Summarization itself costs tokens. Only compact when savings > compaction cost.
- **Model choice for summarization**: Use a cheap model (`gemini-2.5-flash-lite`, `claude-haiku-4-5`) for summarization. Don't use Pro for cleanup tasks.
