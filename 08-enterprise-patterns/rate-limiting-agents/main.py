"""Rate Limiting Agents — token bucket + multi-level rate limiter.
Run: python 08-enterprise-patterns/rate-limiting-agents/main.py
"""
import time


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, burst: int):
        self.rate = rate  # Tokens per second
        self.burst = burst  # Max burst
        self.tokens = float(burst)
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
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


class AgentRateLimiter:
    """Three-level rate limiter: global → agent → user."""

    def __init__(self):
        self.global_bucket = TokenBucket(rate=100, burst=200)
        self.agent_buckets: dict[str, TokenBucket] = {}
        self.user_buckets: dict[str, TokenBucket] = {}

    def allow(self, user_id: str, agent_name: str) -> tuple[bool, str]:
        if not self.global_bucket.consume():
            return False, "global"

        agent_key = f"agent:{agent_name}"
        if agent_key not in self.agent_buckets:
            self.agent_buckets[agent_key] = TokenBucket(rate=10, burst=20)
        if not self.agent_buckets[agent_key].consume():
            return False, "agent"

        user_key = f"user:{user_id}"
        if user_key not in self.user_buckets:
            self.user_buckets[user_key] = TokenBucket(rate=1, burst=5)
        if not self.user_buckets[user_key].consume():
            return False, "user"

        return True, "ok"


def main():
    print("Rate Limiting Demo\n")

    limiter = AgentRateLimiter()

    # Simulate 15 rapid requests from 2 users
    results = {"allowed": 0, "blocked_global": 0, "blocked_agent": 0, "blocked_user": 0}

    for i in range(15):
        for user_id in ["user-1", "user-2"]:
            allowed, level = limiter.allow(user_id, "support-agent")
            if allowed:
                results["allowed"] += 1
                print(f"  Request {i+1} ({user_id}): ✓")
            else:
                results[f"blocked_{level}"] += 1
                print(f"  Request {i+1} ({user_id}): ✗ blocked at {level} level")

    print(f"\nResults: {results['allowed']} allowed, "
          f"{results['blocked_user']} user-limited, "
          f"{results['blocked_agent']} agent-limited, "
          f"{results['blocked_global']} global-limited")


if __name__ == "__main__":
    main()
