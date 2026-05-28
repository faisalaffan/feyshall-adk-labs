# Flutter Agent Widget

> **Status:** Planned. Waiting for official ADK Dart SDK.

## Concept

A reusable Flutter widget that wraps an ADK agent session, handling:

- Chat UI with streaming text
- Tool call progress indicators
- Session persistence
- Error and retry states

## Planned API

```dart
AgentChat(
  agentName: 'customer-support',
  sessionId: 'user-123',
  onToolCall: (tool) => showToolProgress(tool),
  theme: AgentChatTheme(
    userBubble: Colors.blue,
    agentBubble: Colors.grey,
  ),
)
```

## Dependencies

- `adk_client` — thin REST wrapper (see `setup.md`)
- `flutter_bloc` or `riverpod` — state management
- `flutter_markdown` — render agent responses
