---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Tool Error Handling

## Concept

By default, ADK catches tool exceptions and feeds the error message back to the LLM. This "silent failure" pattern is powerful but dangerous — the LLM might ignore errors or hallucinate fixes. Explicit error handling gives you control.

## The Default Behavior

```python
def flaky_tool(city: str) -> dict:
    """Get weather. Sometimes fails."""
    if random.random() < 0.3:
        raise RuntimeError("Weather API timeout")
    return {"city": city, "temp": 30}

# LLM receives: "Tool 'flaky_tool' returned error: Weather API timeout"
# LLM might: retry, apologize, or hallucinate weather data
```

## Retry Pattern

```python
import time
from functools import wraps

def with_retries(max_retries: int = 3, backoff: float = 1.0):
    """Decorator: retry tool on failure with exponential backoff."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries:
                        wait = backoff * (2 ** attempt)
                        time.sleep(wait)
            raise last_error
        return wrapper
    return decorator

@with_retries(max_retries=2, backoff=0.5)
def weather_tool(city: str) -> dict:
    """Get weather with automatic retry."""
    return api_call(city)
```

## Graceful Degradation

```python
CACHED_WEATHER = {
    "jakarta": {"temp": 32, "condition": "sunny"},
    "bandung": {"temp": 24, "condition": "cloudy"},
}

def weather_with_fallback(city: str) -> dict:
    """Get weather, fall back to cached data on failure."""
    try:
        return live_api_call(city)
    except Exception as e:
        city_lower = city.lower()
        if city_lower in CACHED_WEATHER:
            return {
                **CACHED_WEATHER[city_lower],
                "stale": True,
                "note": f"Using cached data (API unavailable: {e})",
            }
        return {
            "error": f"Weather unavailable for '{city}'",
            "suggestion": "Try a major city name",
        }
```

## Circuit Breaker

```python
import time
from dataclasses import dataclass

@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    failures: int = 0
    last_failure: float = 0
    open: bool = False

    def call(self, func, *args, **kwargs):
        if self.open:
            if time.time() - self.last_failure > self.recovery_timeout:
                self.open = False  # Half-open — try once
                self.failures = 0
            else:
                return {"error": "Tool temporarily unavailable (circuit open)"}

        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.failure_threshold:
                self.open = True
            raise e
```

## Error Handling Decision Tree

```
Tool fails
├── Transient error (timeout, rate limit)?
│   └── Retry with backoff (max 3 attempts)
│
├── Non-critical data?
│   └── Return cached/default value with stale flag
│
├── Repeated failures (5+ in 60s)?
│   └── Open circuit breaker — fail fast
│
└── Critical failure?
    └── Raise clear error → LLM sees it → LLM informs user
```

## Pitfalls

- **Don't catch everything**: Catching `Exception` in tools hides bugs. Catch specific exceptions you can handle; let unexpected ones propagate.
- **Retry amplification**: If the LLM retries the tool AND your code retries, you get n×m calls. Pick one retry layer — prefer tool-level for transient errors.
- **Silent fallbacks mislead**: If you return stale data, always mark it (`"stale": true`). The LLM can then decide whether to inform the user.
- **Circuit breaker state is per-process**: In multi-instance deployments, each instance has its own circuit state. Use Redis for shared circuit state.
