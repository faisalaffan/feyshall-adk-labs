# ADK Cookbook — Public Roadmap

This is the public summary of the [feyshall-adk-labs](https://github.com/faisalaffan/feyshall-adk-labs) cookbook.

## What This Is

A production-focused cookbook for Google Agent Development Kit (ADK). Every recipe includes:

- **Concept** — what problem this solves and when to use it
- **Runnable code** — copy-paste ready, tested against ADK v1.28
- **Pitfalls** — edge cases and gotchas from real production experience

## Chapter Overview

| Chapter                     | Focus                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------ |
| `00-foundations`            | ADK concepts, lifecycle, model configuration, hello-world in 4 languages                   |
| `01-tools`                  | Function tools, built-in tools, MCP integration, auth, error handling                      |
| `02-multi-agent`            | Sequential, parallel, hierarchical orchestration, routing, circuit breakers                |
| `03-memory-and-state`       | Sessions, Redis backend, vector memory, context compaction                                 |
| `04-streaming`              | SSE, bidirectional audio, tool progress, Next.js + Flutter frontends                       |
| `05-evaluation-and-testing` | Unit testing, eval metrics, CI pipelines, prompt injection testing                         |
| `06-observability`          | OpenTelemetry, LGTM stack, custom metrics, behavioral alerting                             |
| `07-deployment`             | Docker, Kubernetes, Vertex AI, Cloud Run, environment config                               |
| `08-enterprise-patterns`    | Multi-tenancy, RBAC, audit logging, rate limiting, cost management                         |
| `09-real-world-usecases`    | Inventory forecasting, customer support, code review, document processing, ERP, e-commerce |

## Language Support

| Language | Coverage                                                     |
| -------- | ------------------------------------------------------------ |
| Python   | All recipes                                                  |
| Go       | Foundations, tools, deployment                               |
| Java     | Foundations, tools, deployment                               |
| Dart     | REST wrapper + Flutter widget (unique — no official SDK yet) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

See [LICENSE](LICENSE).
