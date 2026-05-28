---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Rate Limiting Agents

## Concept

Without rate limits, a runaway agent can exhaust your API quota, rack up costs, or DoS your own infrastructure. Rate limits protect both your budget and your users.

## Token Bucket Algorithm

```python
import time
from dataclasses import dataclass

@dataclass
class TokenBucket:
    rate: float         # Tokens per second
    burst: int          # Maximum burst size
    tokens: float = 0
    last_refill: float = 0

    def __post_init__(self):
        self.tokens = self.burst
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        self.last_refill = now
```

## Multi-Level Rate Limiter

```python
class AgentRateLimiter:
    """Rate limit at user, agent, and global levels."""

    def __init__(self):
        self.global_bucket = TokenBucket(rate=100, burst=200)    # 100 req/s global
        self.agent_buckets = {}   # Per-agent
        self.user_buckets = {}    # Per-user

    def allow(self, user_id: str, agent_name: str) -> bool:
        # Check global first (fail fast)
        if not self.global_bucket.consume():
            return False

        # Check per-agent
        agent_key = f"agent:{agent_name}"
        if agent_key not in self.agent_buckets:
            self.agent_buckets[agent_key] = TokenBucket(rate=10, burst=20)
        if not self.agent_buckets[agent_key].consume():
            return False

        # Check per-user
        user_key = f"user:{user_id}"
        if user_key not in self.user_buckets:
            self.user_buckets[user_key] = TokenBucket(rate=1, burst=5)
        if not self.user_buckets[user_key].consume():
            return False

        return True
```

## Rate Limit Response

```python
def rate_limited_agent(user_id: str, agent_name: str, user_input: str):
    if not limiter.allow(user_id, agent_name):
        return {
            "error": "rate_limited",
            "retry_after_seconds": 5,
            "message": "Too many requests. Please wait and try again.",
        }

    return run_agent(agent, user_input)
```

## Rate Limit Architecture

```
Request → Global limit (100/s)
              │
              ▼
         Agent limit (10/s per agent)
              │
              ▼
         User limit (1/s per user)
              │
              ▼
         Execute agent
```

## Pitfalls

- **Distributed rate limiting**: The in-memory `TokenBucket` doesn't work across multiple server instances. Use Redis (`INCR` + `EXPIRE`) for multi-instance deployments.
- **429 feedback loop**: If the LLM sees a "rate limited" error and retries immediately, it creates a tight retry loop. Always include `retry_after_seconds` in the error response.
- **Too-strict user limits**: A 1 req/s per-user limit feels broken for power users. Implement tiered limits (free: 1/s, pro: 5/s, enterprise: 20/s).
- **Silent dropping**: Don't silently drop requests. Always return a clear error with retry instructions.
