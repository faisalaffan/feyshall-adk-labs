---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Failure Isolation

## Concept

In multi-agent systems, one failing agent shouldn't take down the entire workflow. Circuit breakers, timeouts, and fallbacks prevent cascading failures.

## Per-Agent Timeout

```python
import asyncio

async def agent_with_timeout(agent, input_text, timeout_seconds: float = 30):
    """Run an agent with a hard deadline."""
    try:
        result = await asyncio.wait_for(
            run_agent_async(agent, input_text),
            timeout=timeout_seconds,
        )
        return {"status": "ok", "result": result}
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "fallback": f"[{agent.name} timed out after {timeout_seconds}s]",
        }
```

## Circuit Breaker for Agents

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, reject immediately
    HALF_OPEN = "half_open" # Testing recovery

class AgentCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time: float = 60):
        self.threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure = 0
        self.state = CircuitState.CLOSED

    async def call(self, agent, input_text):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure > self.recovery_time:
                self.state = CircuitState.HALF_OPEN
            else:
                return {"status": "circuit_open", "result": None}

        try:
            result = await run_agent_async(agent, input_text)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
            return {"status": "ok", "result": result}

        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = CircuitState.OPEN
            return {"status": "error", "error": str(e)}
```

## Graceful Degradation Pattern

```python
def multi_agent_with_fallbacks(user_input: str) -> str:
    """Run agents with per-agent fallbacks."""
    results = {}

    # Primary: full analysis
    sentiment_result = cb_sentiment.call(sentiment_agent, user_input)
    results["sentiment"] = sentiment_result.get("result") or "neutral"

    # If entity extraction fails, use simple regex fallback
    entity_result = cb_entities.call(entities_agent, user_input)
    if entity_result["status"] == "ok":
        results["entities"] = entity_result["result"]
    else:
        results["entities"] = regex_entity_extraction(user_input)
        results["entities_note"] = "Fallback extraction (agent unavailable)"

    return compose_response(results)
```

## Failure Mode Checklist

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Agent timeout | `asyncio.TimeoutError` | Return partial results |
| Agent crash (5xx) | Circuit breaker trip | Route to fallback agent |
| Rate limit | `ResourceExhausted` exception | Exponential backoff |
| Bad output format | JSON parse error | Retry once, then use default |
| LLM hallucination | Confidence < threshold | Escalate to human |

## Pitfalls

- **Too many fallbacks**: If every agent degrades, the user gets a useless response. Define a "minimum viable" output.
- **Hidden failures**: Silent fallbacks mask systemic problems. Log every circuit breaker trip and review daily.
- **Half-open state thrashing**: If the agent is still broken, half-open will fail again. Set a minimum time between half-open attempts.
