import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:adk_client/adk_client.dart';

/// A reusable Flutter widget for chatting with an ADK agent.
///
/// Handles streaming text display, tool call progress indicators,
/// session persistence, and error/retry states.
class AgentChat extends StatefulWidget {
  final AdkClient client;
  final String agentName;
  final String userId;
  final AgentChatTheme? theme;
  final Widget? emptyState;
  final String? initialMessage;

  const AgentChat({
    super.key,
    required this.client,
    required this.agentName,
    required this.userId,
    this.theme,
    this.emptyState,
    this.initialMessage,
  });

  @override
  State<AgentChat> createState() => _AgentChatState();
}

class _AgentChatState extends State<AgentChat> {
  final List<ChatMessage> _messages = [];
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  String? _sessionId;
  bool _isLoading = false;
  bool _isStreaming = false;
  String _streamingText = '';
  Timer? _sessionTimer;
  StreamSubscription<AdkEvent>? _streamSubscription;

  @override
  void initState() {
    super.initState();
    _initSession();
    if (widget.initialMessage != null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _sendMessage(widget.initialMessage!);
      });
    }
  }

  Future<void> _initSession() async {
    _sessionId = await widget.client.createSession(
      appName: widget.agentName,
      userId: widget.userId,
    );
    // Refresh session every 30 min
    _sessionTimer = Timer.periodic(
      const Duration(minutes: 30),
      (_) => _refreshSession(),
    );
  }

  Future<void> _refreshSession() async {
    if (!mounted) return;
    _sessionId = await widget.client.createSession(
      appName: widget.agentName,
      userId: widget.userId,
    );
  }

  Future<void> _sendMessage(String text) async {
    if (text.trim().isEmpty || _sessionId == null) return;

    final userMessage = ChatMessage(
      role: ChatRole.user,
      text: text.trim(),
      timestamp: DateTime.now(),
    );

    setState(() {
      _messages.add(userMessage);
      _streamingText = '';
      _isLoading = true;
      _isStreaming = true;
    });

    _inputController.clear();
    _scrollToBottom();

    final assistantMessage = ChatMessage(
      role: ChatRole.assistant,
      text: '',
      timestamp: DateTime.now(),
      isStreaming: true,
    );
    setState(() => _messages.add(assistantMessage));

    try {
      final stream = widget.client.runAgentStreaming(
        agentName: widget.agentName,
        userInput: text,
        sessionId: _sessionId!,
      );

      _streamSubscription = stream.listen(
        (event) {
          if (!mounted) return;
          setState(() {
            switch (event.type) {
              case AdkEventType.text:
                final chunk = event.text ?? '';
                _streamingText += chunk;
                _messages.last.text = _streamingText;
              case AdkEventType.toolCall:
                final toolName = event.toolCall?.name ?? 'unknown';
                _messages.last.toolCalls.add(
                  ToolCallProgress(
                    name: toolName,
                    status: 'running',
                  ),
                );
                _streamingText += '\n\n🔧 *Running $toolName...*';
                _messages.last.text = _streamingText;
              case AdkEventType.error:
                _streamingText += '\n\n⚠️ Error: ${event.text}';
                _messages.last.text = _streamingText;
            }
          });
          _scrollToBottom();
        },
        onDone: () {
          if (!mounted) return;
          setState(() {
            _messages.last.isStreaming = false;
            _isLoading = false;
            _isStreaming = false;
          });
        },
        onError: (error) {
          if (!mounted) return;
          setState(() {
            _messages.last.text = 'Error: $error';
            _messages.last.isStreaming = false;
            _isLoading = false;
            _isStreaming = false;
          });
        },
      );
    } on AdkException catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.last.text = 'API Error (${e.statusCode}): ${e.message}';
        _messages.last.isStreaming = false;
        _isLoading = false;
        _isStreaming = false;
      });
    }
  }

  Future<void> _retryLastMessage() async {
    if (_messages.isEmpty) return;
    final lastUserMessage = _messages
        .where((m) => m.role == ChatRole.user)
        .lastOrNull;
    if (lastUserMessage != null) {
      _messages.removeWhere((m) => m.role == ChatRole.assistant);
      await _sendMessage(lastUserMessage.text);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 100),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    _sessionTimer?.cancel();
    _streamSubscription?.cancel();
    widget.client.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = widget.theme ?? AgentChatTheme.defaultTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return Column(
      children: [
        // Messages
        Expanded(
          child: _messages.isEmpty
              ? (widget.emptyState ?? _buildEmptyState(theme))
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    return _buildMessage(
                      _messages[index],
                      theme,
                      colorScheme,
                    );
                  },
                ),
        ),

        // Error banner
        if (_messages.isNotEmpty &&
            _messages.last.role == ChatRole.assistant &&
            _messages.last.hasError)
          _buildErrorBanner(theme),

        // Input area
        _buildInputArea(theme, colorScheme),
      ],
    );
  }

  Widget _buildEmptyState(AgentChatTheme theme) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.smart_toy, size: 64, color: theme.botIconColor),
            const SizedBox(height: 16),
            Text(
              'Chat with ${widget.agentName}',
              style: theme.emptyStateStyle,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMessage(
    ChatMessage message,
    AgentChatTheme theme,
    ColorScheme colorScheme,
  ) {
    final isUser = message.role == ChatRole.user;

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isUser ? theme.userBubbleColor : theme.botBubbleColor,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (message.text.contains('##') || message.text.contains('**'))
              MarkdownBody(
                data: _stripStreamingArtifacts(message.text),
                styleSheet: MarkdownStyleSheet(
                  p: TextStyle(color: isUser ? Colors.white : colorScheme.onSurface),
                  strong: TextStyle(
                    color: isUser ? Colors.white : colorScheme.onSurface,
                    fontWeight: FontWeight.bold,
                  ),
                  code: TextStyle(
                    color: isUser ? Colors.white70 : colorScheme.primary,
                    backgroundColor: isUser
                        ? Colors.white.withValues(alpha: 0.2)
                        : colorScheme.surfaceVariant,
                  ),
                ),
              )
            else
              Text(
                _stripStreamingArtifacts(message.text),
                style: TextStyle(color: isUser ? Colors.white : colorScheme.onSurface),
              ),

            // Tool call indicators
            if (message.toolCalls.isNotEmpty) ...[
              const SizedBox(height: 8),
              ...message.toolCalls.map((tc) => _buildToolCallChip(tc, theme)),
            ],

            // Streaming indicator
            if (message.isStreaming)
              Padding(
                padding: const EdgeInsets.only(top: 4),
                child: SizedBox(
                  width: 24,
                  height: 4,
                  child: LinearProgressIndicator(
                    borderRadius: BorderRadius.circular(2),
                    color: isUser ? Colors.white70 : theme.streamingIndicatorColor,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildToolCallChip(ToolCallProgress tc, AgentChatTheme theme) {
    return Container(
      margin: const EdgeInsets.only(top: 4),
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: theme.toolCallChipColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.build, size: 12, color: theme.toolCallChipTextColor),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              tc.name,
              style: TextStyle(fontSize: 11, color: theme.toolCallChipTextColor),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorBanner(AgentChatTheme theme) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      color: theme.errorBannerColor,
      child: Row(
        children: [
          Icon(Icons.error_outline, size: 16, color: theme.errorTextColor),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              'Something went wrong with the last response.',
              style: TextStyle(fontSize: 13, color: theme.errorTextColor),
            ),
          ),
          TextButton(
            onPressed: _retryLastMessage,
            child: Text('Retry', style: TextStyle(color: theme.errorTextColor)),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea(AgentChatTheme theme, ColorScheme colorScheme) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colorScheme.surface,
        border: Border(top: BorderSide(color: colorScheme.surfaceVariant)),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _inputController,
                enabled: !_isLoading,
                decoration: InputDecoration(
                  hintText: 'Type a message...',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                  filled: true,
                  fillColor: colorScheme.surfaceVariant.withValues(alpha: 0.5),
                ),
                onSubmitted: _sendMessage,
              ),
            ),
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: _isLoading
                  ? colorScheme.surfaceVariant
                  : theme.sendButtonColor,
              child: IconButton(
                icon: Icon(
                  _isLoading ? Icons.hourglass_top : Icons.send,
                  color: _isLoading ? colorScheme.onSurface : Colors.white,
                  size: 20,
                ),
                onPressed:
                    _isLoading ? null : () => _sendMessage(_inputController.text),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _stripStreamingArtifacts(String text) {
    return text
        .replaceAll('data: ', '')
        .replaceAll('[DONE]', '')
        .trim();
  }
}

/// Theme configuration for AgentChat widget.
class AgentChatTheme {
  final Color userBubbleColor;
  final Color botBubbleColor;
  final Color sendButtonColor;
  final Color botIconColor;
  final Color streamingIndicatorColor;
  final Color toolCallChipColor;
  final Color toolCallChipTextColor;
  final Color errorBannerColor;
  final Color errorTextColor;
  final TextStyle? emptyStateStyle;

  const AgentChatTheme({
    required this.userBubbleColor,
    required this.botBubbleColor,
    required this.sendButtonColor,
    required this.botIconColor,
    required this.streamingIndicatorColor,
    required this.toolCallChipColor,
    required this.toolCallChipTextColor,
    required this.errorBannerColor,
    required this.errorTextColor,
    this.emptyStateStyle,
  });

  static const defaultTheme = AgentChatTheme(
    userBubbleColor: Color(0xFF1A73E8),
    botBubbleColor: Color(0xFFF1F3F4),
    sendButtonColor: Color(0xFF1A73E8),
    botIconColor: Color(0xFF1A73E8),
    streamingIndicatorColor: Color(0xFF1A73E8),
    toolCallChipColor: Color(0xFFE8F0FE),
    toolCallChipTextColor: Color(0xFF1967D2),
    errorBannerColor: Color(0xFFFFF3E0),
    errorTextColor: Color(0xFFE65100),
    emptyStateStyle: TextStyle(fontSize: 16, color: Color(0xFF5F6368)),
  );
}

/// Role of a chat message.
enum ChatRole { user, assistant }

/// A single message in the chat.
class ChatMessage {
  final ChatRole role;
  String text;
  final DateTime timestamp;
  bool isStreaming;
  final List<ToolCallProgress> toolCalls;

  ChatMessage({
    required this.role,
    required this.text,
    required this.timestamp,
    this.isStreaming = false,
    this.toolCalls = const [],
  });

  bool get hasError => text.contains('Error:') || text.contains('API Error');
}

/// Progress indicator for a tool call during streaming.
class ToolCallProgress {
  final String name;
  final String status;

  ToolCallProgress({required this.name, required this.status});
}
