---
adk_version: "1.28"
level: advanced
languages: [python]
---

# LGTM Stack Integration

## Concept

LGTM (Loki + Grafana + Tempo + VictoriaMetrics) is the de facto open-source observability stack. Connect your ADK agents for logs, metrics, traces, and dashboards.

## Stack Components

```
ADK Agent
    │
    ├── Logs ───────► Loki (via Promtail)
    ├── Metrics ────► VictoriaMetrics (Prometheus-compatible)
    └── Traces ─────► Tempo (OTLP)
            │
            ▼
        Grafana (unified dashboards)
```

## Docker Compose

```yaml
version: "3.8"
services:
  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]

  tempo:
    image: grafana/tempo:latest
    ports: ["4317:4317"]  # OTLP gRPC

  victoria-metrics:
    image: victoriametrics/victoria-metrics:latest
    ports: ["8428:8428"]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      GF_AUTH_ANONYMOUS_ENABLED: "true"
```

## Agent Configuration

```python
import logging
import prometheus_client as prom
from google.adk.telemetry import configure_opentelemetry

# 1. Structured logging for Loki
logging.basicConfig(
    format='{"time":"%(asctime)s","level":"%(levelname)s","agent":"%(agent)s","msg":"%(message)s"}',
    handlers=[logging.FileHandler("/var/log/agent.jsonl")],
)

# 2. Custom metrics for VictoriaMetrics
tool_calls = prom.Counter("adk_tool_calls_total", "Total tool calls", ["tool_name"])
tool_latency = prom.Histogram("adk_tool_latency_seconds", "Tool latency", ["tool_name"])
llm_tokens = prom.Counter("adk_llm_tokens_total", "Total tokens", ["model", "type"])

# 3. Traces to Tempo
configure_opentelemetry(
    exporter=OTLPSpanExporter(endpoint="http://tempo:4317"),
    service_name="adk-agent",
)
```

## Essential Dashboard Panels

| Panel | Metric | Why |
|-------|--------|-----|
| Tool calls/sec | `rate(adk_tool_calls_total[5m])` | Throughput |
| Tool latency P95 | `histogram_quantile(0.95, adk_tool_latency_seconds)` | Performance |
| Token usage/hr | `rate(adk_llm_tokens_total[1h])` | Cost |
| Error rate | `rate(adk_tool_errors_total[5m])` | Reliability |
| Agent loop count | `adk_agent_turns_total` | Complexity |

## Pitfalls

- **Loki label cardinality**: Don't put user_id or session_id as Loki labels. Use structured log fields instead.
- **VictoriaMetrics storage**: Metrics accumulate fast. Set retention policies (`--retentionPeriod=30d`).
- **Tempo trace sampling**: 100% sampling in production is expensive. Sample 10% and up-sample errors to 100%.
