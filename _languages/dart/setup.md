# Dart Setup

> **Note:** No official ADK Dart SDK yet. Until one is available, use a thin REST wrapper around the ADK API.

## Prerequisites

- Dart 3.0+
- Flutter 3.16+ (for Flutter recipes)

## Approach

ADK exposes a REST API. We wrap it with a lightweight Dart client:

```dart
// lib/adk_client.dart (planned)
class AdkClient {
  final String baseUrl;
  final String apiKey;

  Future<AgentResponse> runAgent(String agentName, String input) async {
    // POST to ADK REST endpoint
  }
}
```

## Limitations

- No streaming support via REST wrapper (use raw SSE until SDK is ready)
- Tool definitions must be serialized to JSON schema manually
- Session management is client-side

## Environment Variables

```bash
export ADK_API_URL="http://localhost:8080"
export GOOGLE_API_KEY="your-api-key"
```
