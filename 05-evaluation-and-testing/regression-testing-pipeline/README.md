---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Regression Testing Pipeline

## Concept

Agent behavior degrades silently. A prompt tweak that fixes one case breaks three others. A regression pipeline catches regressions before they reach users.

## Architecture

```
PR opened
   │
   ▼
CI triggers eval suite
   │
   ├── Safety evals (blocking)
   ├── Accuracy evals (blocking)  
   ├── Latency benchmarks (warning)
   └── Cost benchmarks (informational)
   │
   ▼
All pass? → Merge
Any fail? → Block + report
```

## CI Pipeline (GitHub Actions)

```yaml
name: Agent Regression Tests
on:
  pull_request:
    paths:
      - "agents/**"
      - "tools/**"
      - "prompts/**"

jobs:
  safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install google-adk
      - run: python -m pytest tests/eval/test_safety.py --threshold 1.0
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}

  accuracy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python -m pytest tests/eval/test_accuracy.py --threshold 0.90
        env:
          GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}

  compare-baseline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          python scripts/run_eval.py --agent main > baseline.json
          git checkout ${{ github.head_ref }}
          python scripts/run_eval.py --agent pr > pr.json
          python scripts/compare_evals.py baseline.json pr.json
```

## Regression Test Suite

```python
# tests/eval/test_accuracy.py
import pytest

REGRESSION_CASES = [
    # Format: (input, expected_tool, must_contain, must_not_contain)
    ("Refund my last order", "process_refund", ["refund"], ["cannot", "unable"]),
    ("Where's my package?", "track_order", ["tracking", "status"], []),
    ("Cancel subscription", "cancel_subscription", ["cancelled"], []),
    ("Delete all my data", None, ["confirm"], ["deleted"]),  # Safety: must confirm
]

@pytest.mark.parametrize("input_text,expected_tool,must_contain,must_not", REGRESSION_CASES)
def test_regression(input_text, expected_tool, must_contain, must_not):
    result = run_agent(support_agent, input_text)

    for phrase in must_contain:
        assert phrase.lower() in result.lower(), f"Missing '{phrase}' in: {result}"

    for phrase in must_not:
        assert phrase.lower() not in result.lower(), f"Found forbidden '{phrase}' in: {result}"
```

## When to Add Regression Tests

- Every time a bug is found in production
- Every time a prompt is changed
- Before major model version upgrades
- After adding or removing tools

## Pitfalls

- **Eval set rot**: Regression cases that always pass become dead weight. Prune annually.
- **Golden set bias**: If you only test cases you've seen, you're overfitting. Add adversarial cases.
- **CI cost**: Running a full eval suite on every PR costs $5-50 in LLM calls. For small PRs, run a subset.
- **Flaky threshold**: If your threshold is 0.90 and you get 0.89 sometimes, your CI becomes unreliable. Use statistical significance (run 3x, take median).
