---
adk_version: "1.28"
level: advanced
languages: [python]
---

# OpenTelemetry Setup

## Concept

OpenTelemetry (OTel) gives you distributed traces across your agent stack: LLM calls, tool invocations, and external API requests. Standard setup for production observability.

## Installation

```bash
pip install google-adk[opentelemetry]
pip install opentelemetry-exporter-otlp
```

## Configuration

```python
from google.adk.telemetry import configure_opentelemetry
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

configure_opentelemetry(
    exporter=OTLPSpanExporter(endpoint="http://localhost:4317"),
    service_name="adk-agent-service",
    span_processor=BatchSpanProcessor,
)

# Now all agent runs automatically create traces
agent = Agent(name="my-agent", model="gemini-2.5-flash")
# Every run_agent() call produces spans:
# agent.run → llm.generate → tool.execute → tool.api_call
```

## What You Get

```
Trace: agent-run-abc123 (4.2s total)
├── Span: llm.generate (1.2s)
│   ├── input_tokens: 450
│   └── output_tokens: 120
├── Span: tool.get_weather (0.8s)
│   ├── tool.name: get_weather
│   └── tool.args: {"city": "Jakarta"}
├── Span: http.api.openweathermap (0.5s)
│   └── http.status_code: 200
└── Span: llm.generate (1.5s)
    ├── input_tokens: 680
    └── output_tokens: 85
```

## Custom Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def weather_tool(city: str) -> dict:
    with tracer.start_as_current_span("weather_api_call") as span:
        span.set_attribute("city", city)
        span.set_attribute("provider", "openweathermap")

        result = call_weather_api(city)

        span.set_attribute("temperature", result["temp"])
        span.set_attribute("status", "success")
        return result
```

## Pitfalls

- **Span explosion**: Each tool call creates a span. 5 tools × 10 requests/s = 50 spans/s. Set sampling rates for production.
- **Exporter latency**: The OTLP exporter sends spans asynchronously, but batch processing adds 1-5s. For real-time debugging, use console exporter in dev.
- **Sensitive data in spans**: Tool arguments (including API keys, user emails) become span attributes. Use `span.set_attribute("user.email", hash(email))`, never raw values.
