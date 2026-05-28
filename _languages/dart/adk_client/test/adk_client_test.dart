import 'package:test/test.dart';
import 'package:adk_client/adk_client.dart';

void main() {
  group('AdkClient', () {
    test('constructor sets baseUrl and apiKey', () {
      final client = AdkClient(
        baseUrl: 'http://localhost:8080',
        apiKey: 'test-key',
      );
      expect(client.baseUrl, 'http://localhost:8080');
      expect(client.apiKey, 'test-key');
    });

    test('healthCheck handles connection refused gracefully', () async {
      final client = AdkClient(
        baseUrl: 'http://localhost:1', // Nothing listening here
        apiKey: 'test-key',
      );
      final healthy = await client.healthCheck();
      expect(healthy, isFalse);
    });

    test('AdkResponse parses flat output format', () {
      final response = AdkResponse.fromJson({
        'output': 'Hello, World!',
        'tool_calls': [],
      });
      expect(response.text, 'Hello, World!');
      expect(response.toolCalls, isEmpty);
    });

    test('AdkResponse parses nested output format', () {
      final response = AdkResponse.fromJson({
        'text': 'Hello!',
        'tool_calls': [
          {
            'name': 'greet',
            'args': {'name': 'Faisal'},
            'result': 'Hello, Faisal!',
          }
        ],
      });
      expect(response.text, 'Hello!');
      expect(response.toolCalls.length, 1);
      expect(response.toolCalls[0].name, 'greet');
      expect(response.toolCalls[0].arguments['name'], 'Faisal');
    });

    test('AdkEvent parses text event', () {
      final event = AdkEvent.fromJson({'text': 'Hello chunk'});
      expect(event.type, AdkEventType.text);
      expect(event.text, 'Hello chunk');
    });

    test('AdkEvent parses tool_call event', () {
      final event = AdkEvent.fromJson({
        'tool_call': {'name': 'greet', 'arguments': {'name': 'Test'}},
      });
      expect(event.type, AdkEventType.toolCall);
      expect(event.toolCall?.name, 'greet');
    });

    test('AdkException formatting', () {
      final ex = AdkException(statusCode: 429, message: 'Rate limited');
      expect(ex.toString(), contains('429'));
      expect(ex.toString(), contains('Rate limited'));
    });
  });
}
