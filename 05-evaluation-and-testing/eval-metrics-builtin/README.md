---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Eval Metrics (Built-in)

## Concept

ADK ships with built-in evaluation metrics for common quality checks. Use these before building custom evals — they cover 80% of what you need.

## Available Metrics

```python
from google.adk.evaluation import (
    ToolUseAccuracy,
    ResponseRelevance,
    FactualCorrectness,
    SafetyScore,
)

eval_set = [
    {
        "input": "What's the return policy?",
        "expected_tool": "lookup_return_policy",
        "expected_contains": ["30 days", "original packaging"],
    },
    {
        "input": "Where is my order?",
        "expected_tool": "track_order",
        "expected_contains": ["tracking", "status"],
    },
]

results = evaluate(
    agent=support_agent,
    eval_set=eval_set,
    metrics=[
        ToolUseAccuracy(),       # Did agent call the right tool?
        ResponseRelevance(),     # Is the response on-topic?
        FactualCorrectness(),    # Are facts correct? (needs ground truth)
        SafetyScore(),           # Any safety violations?
    ],
)

print(f"Tool accuracy: {results['ToolUseAccuracy']:.1%}")
print(f"Relevance: {results['ResponseRelevance']:.1%}")
print(f"Factual: {results['FactualCorrectness']:.1%}")
print(f"Safety: {results['SafetyScore']:.1%}")
```

## Metric Definitions

| Metric | What It Measures | Requires |
|--------|-----------------|----------|
| `ToolUseAccuracy` | Did agent call expected tool? | Expected tool name |
| `ResponseRelevance` | Is response on-topic? | Nothing (LLM-judged) |
| `FactualCorrectness` | Are facts correct? | Ground truth answer |
| `SafetyScore` | Any harmful/toxic content? | Nothing (classifier) |
| `LatencyP50/P95` | Response time distribution | Nothing |

## Running Evals in CI

```yaml
# .github/workflows/eval.yml
name: Agent Evaluation
on:
  pull_request:
    paths: ["agents/**", "tools/**"]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install google-adk pytest
      - run: python -m pytest tests/eval/ --eval-threshold 0.85
```

## Pitfalls

- **LLM-judged metrics are stochastic**: Running the same eval twice can give different scores. Set a threshold, not an exact number.
- **Eval set contamination**: If your eval questions leak into training data, metrics become meaningless. Keep eval sets private.
- **Metrics != user satisfaction**: High tool accuracy doesn't mean users are happy. Pair automated evals with user feedback.
