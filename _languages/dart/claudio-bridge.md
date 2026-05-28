# Claudio Bridge

> **Status:** Planned. Unique angle — bridging Dart/Flutter with ADK via a lightweight middleware.

## Concept

Claudio is a thin bridge that lets Flutter apps talk to ADK agents without direct REST calls. It handles:

- Agent discovery and routing
- Streaming response adaptation (SSE → Flutter streams)
- Tool call serialization (Dart ↔ JSON Schema)
- Offline queue (queue actions when disconnected, replay on reconnect)

## Architecture

```
Flutter App
    │
    ▼
Claudio (Dart package)
    │
    ▼
ADK REST API / gRPC
    │
    ▼
Agent Runtime
```

## Why "Claudio"

Named after Claudio Monteverdi, who bridged Renaissance and Baroque music — this bridges Flutter and the agent ecosystem.
