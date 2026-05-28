---
adk_version: "1.28"
level: intermediate
languages: [dart]
---

# First Agent — Hello World (Dart)

> **Status:** Planned. No official ADK Dart SDK exists yet. This recipe uses a thin REST wrapper until the SDK is available.

## Concept

Until Google releases an official ADK Dart SDK, we communicate with the ADK REST API. The wrapper handles JSON serialization, session management, and SSE streaming.

## Prerequisites

```bash
dart pub add http
export ADK_API_URL="http://localhost:8080"
export GOOGLE_API_KEY="your-api-key"
```

## Code (REST Wrapper)

```dart
// lib/adk_client.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AdkClient {
  final String baseUrl;
  final String apiKey;
  final http.Client _client;

  AdkClient({required this.baseUrl, required this.apiKey})
      : _client = http.Client();

  Future<String> runAgent({
    required String agentName,
    required String userInput,
    required String sessionId,
  }) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/agents/$agentName/run'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
      },
      body: jsonEncode({
        'input': userInput,
        'session_id': sessionId,
      }),
    );

    if (response.statusCode != 200) {
      throw AdkException('ADK request failed: ${response.body}');
    }

    final data = jsonDecode(response.body);
    return data['output'] as String;
  }

  void close() => _client.close();
}

class AdkException implements Exception {
  final String message;
  AdkException(this.message);
}
```

## Code (Usage)

```dart
// main.dart
import 'adk_client.dart';

void main() async {
  final client = AdkClient(
    baseUrl: 'http://localhost:8080',
    apiKey: 'your-api-key',
  );

  try {
    final response = await client.runAgent(
      agentName: 'hello-world',
      userInput: 'My name is Faisal',
      sessionId: 'user-1',
    );
    print(response);
  } on AdkException catch (e) {
    print('Error: ${e.message}');
  } finally {
    client.close();
  }
}
```

## Pitfalls

- **No official SDK yet**: This wrapper breaks if ADK REST API changes. Pin your ADK server version.
- **No streaming via REST**: SSE support requires `dart:io` `HttpClient` with streaming response handling — more complex than the simple wrapper above.
- **Tool serialization is manual**: You must serialize Dart function signatures to JSON Schema by hand. See `tool-with-auth/` for patterns.
- **Session persistence**: The REST API is stateless; you must manage session IDs client-side.
