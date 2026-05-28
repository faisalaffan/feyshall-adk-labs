import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;

/// Thin REST wrapper for Google ADK agent runtime.
///
/// Communicates with the ADK REST API for agent invocation,
/// session management, and streaming responses.
class AdkClient {
  final String baseUrl;
  final String apiKey;
  final http.Client _client;

  AdkClient({required this.baseUrl, required this.apiKey})
      : _client = http.Client();

  /// Run an agent synchronously (non-streaming).
  ///
  /// Returns the full agent response as a string.
  Future<AdkResponse> runAgent({
    required String agentName,
    required String userInput,
    required String sessionId,
    String? userId,
  }) async {
    final uri = Uri.parse('$baseUrl/agents/$agentName/run');
    final response = await _client.post(
      uri,
      headers: _headers(),
      body: jsonEncode({
        'input': userInput,
        'session_id': sessionId,
        if (userId != null) 'user_id': userId,
      }),
    );

    if (response.statusCode != 200) {
      throw AdkException(
        statusCode: response.statusCode,
        message: 'ADK request failed: ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return AdkResponse.fromJson(data);
  }

  /// Run an agent with streaming (SSE).
  ///
  /// Yields text chunks and tool calls as they arrive.
  Stream<AdkEvent> runAgentStreaming({
    required String agentName,
    required String userInput,
    required String sessionId,
  }) async* {
    final uri = Uri.parse('$baseUrl/agents/$agentName/run/stream');
    final request = http.Request('POST', uri)
      ..headers.addAll(_headers())
      ..body = jsonEncode({
        'input': userInput,
        'session_id': sessionId,
      });

    final response = await _client.send(request);

    if (response.statusCode != 200) {
      final body = await response.stream.bytesToString();
      throw AdkException(
        statusCode: response.statusCode,
        message: 'ADK streaming request failed: $body',
      );
    }

    await for (final chunk in response.stream
        .transform(utf8.decoder)
        .transform(const LineSplitter())) {
      if (chunk.startsWith('data: ') && chunk != 'data: [DONE]') {
        try {
          final json = jsonDecode(chunk.substring(6)) as Map<String, dynamic>;
          yield AdkEvent.fromJson(json);
        } catch (_) {
          // Skip malformed chunks
        }
      }
    }
  }

  /// Create a new session.
  Future<String> createSession({
    required String appName,
    required String userId,
  }) async {
    final uri = Uri.parse('$baseUrl/sessions');
    final response = await _client.post(
      uri,
      headers: _headers(),
      body: jsonEncode({
        'app_name': appName,
        'user_id': userId,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['session_id'] as String;
    }

    // Fallback: generate client-side session ID
    return '${appName}_${userId}_${DateTime.now().millisecondsSinceEpoch}';
  }

  /// List available agents.
  Future<List<AdkAgentInfo>> listAgents() async {
    final uri = Uri.parse('$baseUrl/agents');
    final response = await _client.get(uri, headers: _headers());

    if (response.statusCode != 200) {
      throw AdkException(
        statusCode: response.statusCode,
        message: 'Failed to list agents: ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final agents = data['agents'] as List<dynamic>? ?? [];
    return agents.map((a) => AdkAgentInfo.fromJson(a as Map<String, dynamic>)).toList();
  }

  /// Health check.
  Future<bool> healthCheck() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await _client.get(uri).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Map<String, String> _headers() => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $apiKey',
      };

  void close() => _client.close();
}

/// Parsed response from a non-streaming agent run.
class AdkResponse {
  final String text;
  final List<AdkToolCall> toolCalls;
  final Map<String, dynamic>? sessionState;

  AdkResponse({
    required this.text,
    this.toolCalls = const [],
    this.sessionState,
  });

  factory AdkResponse.fromJson(Map<String, dynamic> json) {
    // ADK response format can vary; handle both flat and nested
    final output = json['output'] ?? json['text'] ?? '';
    final toolCalls = (json['tool_calls'] as List<dynamic>?)
            ?.map((t) => AdkToolCall.fromJson(t as Map<String, dynamic>))
            .toList() ??
        [];
    return AdkResponse(
      text: output is String ? output : jsonEncode(output),
      toolCalls: toolCalls,
      sessionState: json['session_state'] as Map<String, dynamic>?,
    );
  }
}

/// Streaming event from the agent.
class AdkEvent {
  final AdkEventType type;
  final String? text;
  final AdkToolCall? toolCall;
  final Map<String, dynamic>? metadata;

  AdkEvent({
    required this.type,
    this.text,
    this.toolCall,
    this.metadata,
  });

  factory AdkEvent.fromJson(Map<String, dynamic> json) {
    AdkEventType type;
    if (json.containsKey('tool_call')) {
      type = AdkEventType.toolCall;
    } else if (json.containsKey('error')) {
      type = AdkEventType.error;
    } else {
      type = AdkEventType.text;
    }

    return AdkEvent(
      type: type,
      text: json['text'] as String? ?? json['content'] as String?,
      toolCall: json['tool_call'] != null
          ? AdkToolCall.fromJson(json['tool_call'] as Map<String, dynamic>)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

enum AdkEventType { text, toolCall, error }

/// Info about a specific tool call.
class AdkToolCall {
  final String name;
  final Map<String, dynamic> arguments;
  final String? result;
  final String? error;

  AdkToolCall({
    required this.name,
    required this.arguments,
    this.result,
    this.error,
  });

  factory AdkToolCall.fromJson(Map<String, dynamic> json) {
    return AdkToolCall(
      name: json['name'] as String? ?? json['tool_name'] as String? ?? '',
      arguments: (json['arguments'] as Map<String, dynamic>?) ??
          (json['args'] as Map<String, dynamic>?) ??
          {},
      result: json['result'] as String?,
      error: json['error'] as String?,
    );
  }
}

/// Info about an available agent.
class AdkAgentInfo {
  final String name;
  final String? description;
  final List<String> capabilities;

  AdkAgentInfo({
    required this.name,
    this.description,
    this.capabilities = const [],
  });

  factory AdkAgentInfo.fromJson(Map<String, dynamic> json) {
    return AdkAgentInfo(
      name: json['name'] as String,
      description: json['description'] as String?,
      capabilities: (json['capabilities'] as List<dynamic>?)
              ?.map((c) => c.toString())
              .toList() ??
          [],
    );
  }
}

/// Exception thrown when ADK API calls fail.
class AdkException implements Exception {
  final int statusCode;
  final String message;

  AdkException({required this.statusCode, required this.message});

  @override
  String toString() => 'AdkException($statusCode): $message';
}
