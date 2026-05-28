import 'package:flutter_test/flutter_test.dart';
import 'package:agent_chat/agent_chat.dart';
import 'package:adk_client/adk_client.dart';

void main() {
  group('AgentChatTheme', () {
    test('defaultTheme has non-null colors', () {
      const theme = AgentChatTheme.defaultTheme;
      expect(theme.userBubbleColor, isNotNull);
      expect(theme.botBubbleColor, isNotNull);
      expect(theme.sendButtonColor, isNotNull);
    });
  });

  group('ChatMessage', () {
    test('hasError detects error patterns', () {
      final errorMsg = ChatMessage(
        role: ChatRole.assistant,
        text: 'Error: Connection refused',
        timestamp: DateTime.now(),
      );
      expect(errorMsg.hasError, isTrue);

      final okMsg = ChatMessage(
        role: ChatRole.assistant,
        text: 'Hello, how can I help?',
        timestamp: DateTime.now(),
      );
      expect(okMsg.hasError, isFalse);
    });

    test('toolCalls default to empty', () {
      final msg = ChatMessage(
        role: ChatRole.assistant,
        text: 'Hello',
        timestamp: DateTime.now(),
      );
      expect(msg.toolCalls, isEmpty);
    });
  });

  group('ToolCallProgress', () {
    test('constructor sets name and status', () {
      final tc = ToolCallProgress(name: 'greet', status: 'running');
      expect(tc.name, 'greet');
      expect(tc.status, 'running');
    });
  });
}
