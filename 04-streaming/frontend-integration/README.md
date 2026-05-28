---
adk_version: "1.28"
level: intermediate
languages: [python, dart]
---

# Frontend Integration

## Concept

Consuming agent streams from web and mobile clients. This recipe covers Next.js (React) and Flutter patterns for displaying streaming agent output.

## Next.js (React)

```typescript
// app/api/chat/route.ts
export async function POST(req: Request) {
  const { message } = await req.json();

  const stream = new ReadableStream({
    async start(controller) {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      const reader = response.body!.getReader();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        controller.enqueue(value);
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream" },
  });
}
```

```typescript
// components/ChatBox.tsx
"use client";

export function ChatBox() {
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(message: string) {
    setLoading(true);
    setOutput("");

    const response = await fetch("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });

    const reader = response.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value);
      for (const line of text.split("\n")) {
        if (line.startsWith("data: ") && line !== "data: [DONE]") {
          const { text: chunk } = JSON.parse(line.slice(6));
          setOutput((prev) => prev + chunk);
        }
      }
    }
    setLoading(false);
  }

  return (
    <div>
      <div className="output">{output}</div>
      {loading && <Spinner />}
      <Input onSubmit={send} />
    </div>
  );
}
```

## Flutter

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class AgentChat extends StatefulWidget {
  @override
  State<AgentChat> createState() => _AgentChatState();
}

class _AgentChatState extends State<AgentChat> {
  final _output = StringBuffer();
  var _loading = false;

  Future<void> _send(String message) async {
    setState(() {
      _loading = true;
      _output.clear();
    });

    final response = await http.Client().send(http.Request(
      "POST", Uri.parse("http://10.0.2.2:8000/chat"),
    )..body = jsonEncode({"message": message}));

    response.stream
        .transform(utf8.decoder)
        .transform(const LineSplitter())
        .listen((line) {
      if (line.startsWith("data: ") && line != "data: [DONE]") {
        final data = jsonDecode(line.substring(6));
        setState(() => _output.write(data["text"]));
      }
    }, onDone: () => setState(() => _loading = false));
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: SelectableText(_output.toString())),
        if (_loading) const LinearProgressIndicator(),
        TextField(onSubmitted: _send),
      ],
    );
  }
}
```

## Pitfalls

- **CORS**: The browser blocks requests from `localhost:3000` to `localhost:8000`. Add CORS headers or use a proxy.
- **Mobile emulator networking**: Android emulator uses `10.0.2.2` to reach host `localhost`. iOS simulator uses `localhost` directly.
- **Stream accumulation**: React's `setState` on every token can cause jank. Batch updates with `requestAnimationFrame` or throttle to 30fps.
