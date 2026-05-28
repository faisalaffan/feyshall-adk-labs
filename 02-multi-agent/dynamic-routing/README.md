---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Dynamic Routing

## Concept

Route user input to the right agent based on content, not a predefined workflow. Two approaches: LLM-driven (flexible but slow) and rule-based (fast but rigid).

## LLM-Driven Routing

```python
from google.adk.agents import Agent

router = Agent(
    name="router",
    model="gemini-2.5-flash",
    instruction="""Classify user input into exactly one category:
    - 'billing' — payment, invoice, refund questions
    - 'technical' — bugs, errors, API questions
    - 'account' — login, password, profile questions
    - 'general' — everything else

    Return ONLY the category name, nothing else.""",
)

def llm_route(user_input: str):
    """Classify input with LLM, then dispatch to specialist."""
    category = run_agent(router, user_input).strip().lower()

    specialist_map = {
        "billing": billing_agent,
        "technical": technical_agent,
        "account": account_agent,
        "general": general_agent,
    }

    specialist = specialist_map.get(category, general_agent)
    return run_agent(specialist, user_input)
```

## Rule-Based Routing (Faster)

```python
import re

ROUTING_RULES = [
    (r"(?i)(invoice|payment|refund|charge|billing)", "billing"),
    (r"(?i)(bug|error|crash|500|timeout|api)", "technical"),
    (r"(?i)(login|password|profile|sign.*in|account)", "account"),
]

def rule_route(user_input: str):
    """Regex-based routing. No LLM cost, ~1ms latency."""
    for pattern, category in ROUTING_RULES:
        if re.search(pattern, user_input):
            return category
    return "general"
```

## Hybrid Routing (Recommended)

```python
def hybrid_route(user_input: str, confidence_threshold: float = 0.8):
    """Rule-based first (fast path), LLM fallback (slow path)."""
    rule_result = rule_route(user_input)
    if rule_result != "general":
        return rule_result, "rule"

    llm_result = llm_route(user_input)
    return llm_result, "llm"
```

## Decision Matrix

| Approach | Latency | Cost | Accuracy | Maintenance |
|----------|---------|------|----------|-------------|
| Rule-based | <1ms | Zero | 70-85% | Regex grows complex |
| LLM-driven | 500ms-2s | 1 LLM call | 90-98% | Prompt tuning |
| Hybrid | <1ms (80%) / 500ms (20%) | Low | 95%+ | Both need maintenance |

## Pitfalls

- **LLM routing drift**: As you add categories, the LLM may misclassify. Re-test routing accuracy weekly.
- **Regex false positives**: A user asking "how do I report a bug in my invoice?" matches both `bug` and `invoice`. Use priority ordering.
- **Amplified latency**: LLM routing adds 500ms+ BEFORE the specialist agent runs. Users feel the wait.
