---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Cost Management

## Concept

AI agents can get expensive fast. Without cost controls, a single runaway agent loop or power user can burn through your monthly budget in hours. This recipe covers token budgets, model tier selection, and cost attribution.

## Token Budget per Request

```python
class TokenBudget:
    """Enforce a token budget per agent invocation."""

    def __init__(self, max_input_tokens: int, max_output_tokens: int):
        self.max_input = max_input_tokens
        self.max_output = max_output_tokens
        self.used_input = 0
        self.used_output = 0

    def track_input(self, tokens: int):
        self.used_input += tokens
        if self.used_input > self.max_input:
            raise BudgetExceededError(
                f"Input token budget exceeded: {self.used_input}/{self.max_input}"
            )

    def track_output(self, tokens: int):
        self.used_output += tokens
        if self.used_output > self.max_output:
            raise BudgetExceededError(
                f"Output token budget exceeded: {self.used_output}/{self.max_output}"
            )
```

## Model Tier Selection

```python
MODEL_TIERS = {
    "critical": {
        "model": "gemini-2.5-pro",
        "cost_per_1k_input": 0.00125,
        "cost_per_1k_output": 0.005,
    },
    "default": {
        "model": "gemini-2.5-flash",
        "cost_per_1k_input": 0.00015,
        "cost_per_1k_output": 0.0006,
    },
    "budget": {
        "model": "gemini-2.5-flash-lite",
        "cost_per_1k_input": 0.000075,
        "cost_per_1k_output": 0.0003,
    },
}

def select_model(intent: str, user_tier: str) -> dict:
    """Select model based on task importance and user plan."""
    if user_tier == "enterprise" and intent in ("financial", "medical", "legal"):
        return MODEL_TIERS["critical"]
    elif user_tier == "free":
        return MODEL_TIERS["budget"]
    return MODEL_TIERS["default"]
```

## Cost Attribution

```python
@dataclass
class CostTracker:
    """Track costs per user, agent, and session."""

    def record_usage(self, agent_name, user_id, session_id, model, input_tokens, output_tokens):
        tier = MODEL_TIERS.get(model, MODEL_TIERS["default"])
        cost = (
            input_tokens / 1000 * tier["cost_per_1k_input"]
            + output_tokens / 1000 * tier["cost_per_1k_output"]
        )
        # Write to your billing system
        billing.record({
            "agent": agent_name,
            "user": user_id,
            "session": session_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "timestamp": now(),
        })
```

## Cost Optimization Checklist

- [ ] Use `gemini-2.5-flash` for 90% of requests — it's 8x cheaper than Pro
- [ ] Set `max_output_tokens` explicitly — don't let the model decide
- [ ] Cache frequent LLM responses (semantic cache with embedding similarity)
- [ ] Compress long conversation history (see `context-compaction.md`)
- [ ] Alert when per-user daily cost exceeds threshold
- [ ] Review cost-per-agent weekly — optimize or retire expensive agents

## Cost Reference (May 2026, per 1K tokens)

| Model | Input | Output |
|-------|-------|--------|
| gemini-2.5-flash-lite | $0.000075 | $0.0003 |
| gemini-2.5-flash | $0.00015 | $0.0006 |
| gemini-2.5-pro | $0.00125 | $0.005 |
| claude-haiku-4-5 | $0.0008 | $0.004 |
| claude-sonnet-4-6 | $0.003 | $0.015 |

## Pitfalls

- **Cost of cost tracking**: Tracking every token adds latency. Batch cost events and write asynchronously.
- **Free tier abuse**: Without per-user budgets, a single user can burn thousands of dollars. Set daily caps, not just rate limits.
- **Model pricing changes**: Cloud providers update pricing. Re-check this table monthly.
- **Output tokens are 4x input cost**: Design prompts that produce concise responses. An agent that says "Certainly! Let me help you with that..." before every answer costs 4x more.
