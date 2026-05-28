---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Custom Metrics

## Concept

Beyond traces, you need metrics for dashboards, alerts, and capacity planning. Track token usage, tool latency, error rates, and agent-specific KPIs.

## Essential Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# Counters: things that only go up
tool_calls = Counter("adk_tool_calls_total", "Tool invocations", ["tool_name", "status"])
llm_calls = Counter("adk_llm_calls_total", "LLM API calls", ["model"])
user_requests = Counter("adk_user_requests_total", "User requests", ["agent_name"])

# Histograms: distributions
tool_latency = Histogram("adk_tool_latency_seconds", "Tool execution time", ["tool_name"])
llm_latency = Histogram("adk_llm_latency_seconds", "LLM response time", ["model"])
turn_count = Histogram("adk_turns_per_request", "Agent loop turns per user request")

# Gauges: current values
active_sessions = Gauge("adk_active_sessions", "Currently active sessions")
token_usage_today = Gauge("adk_token_usage_today", "Tokens used today")

# Summaries: pre-computed quantiles (client-side)
request_size = Summary("adk_request_size_bytes", "Request payload size")
```

## Instrumentation Decorator

```python
import time
from functools import wraps

def instrument_tool(func):
    """Decorator: auto-instrument any tool function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            result = func(*args, **kwargs)
            tool_calls.labels(tool_name=func.__name__, status="success").inc()
            return result
        except Exception as e:
            tool_calls.labels(tool_name=func.__name__, status="error").inc()
            raise
        finally:
            elapsed = time.monotonic() - start
            tool_latency.labels(tool_name=func.__name__).observe(elapsed)

    return wrapper

@instrument_tool
def get_weather(city: str) -> dict:
    return call_weather_api(city)
```

## Alerting Rules

```yaml
# prometheus-rules.yml
groups:
  - name: adk_agent_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(adk_tool_calls_total{status="error"}[5m]) > 0.1
        annotations:
          summary: "Tool error rate > 10%"

      - alert: HighLatency
        expr: histogram_quantile(0.95, adk_tool_latency_seconds) > 10
        annotations:
          summary: "P95 tool latency > 10s"

      - alert: CostSpike
        expr: rate(adk_llm_tokens_total[1h]) > 1000000
        annotations:
          summary: "Token usage > 1M/hour — check for runaway agents"

      - alert: AgentLooping
        expr: histogram_quantile(0.95, adk_turns_per_request) > 15
        annotations:
          summary: "P95 turn count > 15 — agents may be looping"
```

## Pitfalls

- **Cardinality explosion**: `tool_name` and `model` are fine as labels. `user_id`, `session_id`, or `query_text` are not — they create unlimited time series.
- **Histogram bucket tuning**: Default buckets (0.005s to 10s) may not fit agent latencies. Customize: `Histogram(..., buckets=[0.1, 0.5, 1, 5, 10, 30, 60])`.
- **Metric collection overhead**: Prometheus client is efficient, but scraping every 15s from 1000 agent instances generates traffic. Use push gateway for batch jobs.
