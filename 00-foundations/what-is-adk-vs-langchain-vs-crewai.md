---
adk_version: "1.28"
level: beginner
languages: [python]
---

# What Is ADK vs LangChain vs CrewAI

## Concept

Google Agent Development Kit (ADK) is a first-party framework for building AI agents that run on Google's infrastructure. Unlike LangChain (general-purpose LLM orchestration) and CrewAI (multi-agent focus), ADK is tightly integrated with Gemini models and Google Cloud — it's **opinionated about the agent loop** rather than being a toolbox.

| | ADK | LangChain | CrewAI |
|---|---|---|---|
| **Philosophy** | Agent-first, Google-native | Toolbox, provider-agnostic | Multi-agent, role-based |
| **Agent Loop** | Built-in, opinionated | DIY with LCEL | Built-in, sequential |
| **Tooling** | FunctionTool, MCP native | 100+ integrations | LangChain tool compat |
| **Streaming** | First-class, SSE/bidirectional | Via callbacks | Limited |
| **Deployment** | Vertex AI Agent Engine, Cloud Run | Self-hosted, LangServe | Self-hosted |
| **Best For** | GCP teams, production agents | Rapid prototyping, many LLMs | Role-playing multi-agent |

## When to Choose ADK

- You're on Google Cloud and want managed infrastructure
- You need Gemini's native streaming (Live API, bidirectional audio)
- You want an opinionated agent loop without wiring up state machines yourself
- You're building enterprise agents that need audit, RBAC, multi-tenancy

## When NOT to Choose ADK

- You need to switch between 5+ model providers frequently
- Your team has deep LangChain investment and existing chains
- You need a lightweight library without Google Cloud coupling

## Pitfalls

- **Vendor lock-in**: ADK agents are portable via LiteLLM, but advanced features (Live API, Vertex) are Google-only.
- **Rapid evolution**: ADK is at v1.28 and APIs shift. Pin your version.
- **Smaller community**: Fewer StackOverflow answers and third-party tutorials than LangChain.
