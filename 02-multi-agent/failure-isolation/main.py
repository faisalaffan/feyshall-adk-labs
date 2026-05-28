"""Failure Isolation — circuit breaker pattern for multi-agent systems.
Run: python 02-multi-agent/failure-isolation/main.py
"""
import os
import time
import random
from enum import Enum
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class AgentCircuitBreaker:
    """Circuit breaker for individual agent calls."""

    def __init__(self, name: str, failure_threshold: int = 3, recovery_time: float = 5.0):
        self.name = name
        self.threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure = 0.0
        self.state = CircuitState.CLOSED
        self.total_calls = 0
        self.total_rejected = 0

    def call(self, func, *args, **kwargs):
        self.total_calls += 1

        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure > self.recovery_time:
                self.state = CircuitState.HALF_OPEN
                print(f"  [{self.name}] Circuit → HALF_OPEN (testing recovery)")
            else:
                self.total_rejected += 1
                raise CircuitOpenError(f"[{self.name}] Circuit OPEN — rejected")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failures = 0
                print(f"  [{self.name}] Circuit → CLOSED (recovered)")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.monotonic()
            if self.failures >= self.threshold:
                self.state = CircuitState.OPEN
                print(f"  [{self.name}] Circuit → OPEN ({self.failures} failures)")
            raise e


class CircuitOpenError(Exception):
    pass


# --- Demo ---
def flaky_api(endpoint: str) -> str:
    """Simulate a flaky external API (50% failure rate)."""
    if random.random() < 0.5:
        raise ConnectionError(f"API timeout for {endpoint}")
    return f"Response from {endpoint}"


def main():
    random.seed(42)
    print("Failure Isolation Demo — Circuit Breaker Pattern\n")

    cb = AgentCircuitBreaker(name="payment-api", failure_threshold=3, recovery_time=3.0)

    for i in range(10):
        try:
            result = cb.call(flaky_api, "/api/payments")
            print(f"  Call {i+1}: ✓ {result}")
        except CircuitOpenError as e:
            print(f"  Call {i+1}: ⊗ {e}")
        except ConnectionError as e:
            print(f"  Call {i+1}: ✗ {e}")

        time.sleep(0.2)

    print(f"\nStats: {cb.total_calls} calls, {cb.total_rejected} rejected "
          f"(saved {cb.total_rejected} failed API calls)")
    print(f"Final state: {cb.state.value}")


if __name__ == "__main__":
    main()
