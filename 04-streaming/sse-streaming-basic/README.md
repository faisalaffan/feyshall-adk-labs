---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# SSE Streaming Basic

## Concept

By default, `runner.run()` returns a generator that yields events as the agent produces them. For web apps, you expose this as Server-Sent Events (SSE) so the browser can render tokens as they arrive.

## FastAPI Integration

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import json

app = FastAPI()
runner = Runner(
    agent=Agent(name="streaming-agent", model="gemini-2.5-flash"),
    session_service=InMemorySessionService(),
)

@app.post("/chat/{user_id}")
async def chat(user_id: str, request: dict):
    session = runner.session_service.create_session(
        app_name="chat", user_id=user_id,
    )

    async def event_stream():
        for event in runner.run(
            user_input=request["message"],
            session=session,
        ):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {json.dumps({'text': part.text})}\n\n"
                    if part.tool_call:
                        yield f"data: {json.dumps({'tool_call': part.tool_call.name})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
```

## Client-Side (JavaScript)

```javascript
const eventSource = new EventSource("/chat/user-123");

fetch("/chat/user-123", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "Tell me a story" }),
}).then(async (response) => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value);
    const lines = text.split("\n");
    for (const line of lines) {
      if (line.startsWith("data: ") && line !== "data: [DONE]") {
        const data = JSON.parse(line.slice(6));
        document.getElementById("output").innerText += data.text;
      }
    }
  }
});
```

## Pitfalls

- **Proxy buffering**: Nginx and Cloudflare buffer responses by default. Add `X-Accel-Buffering: no` header and set `proxy_buffering off;` in nginx.
- **Connection limits**: Browsers limit SSE connections to 6 per domain. For many concurrent users, use HTTP/2.
- **Reconnection**: If the SSE connection drops, the client must re-establish. Send a `id:` field with each event so the client can send `Last-Event-ID` on reconnect.
- **Tool call streaming**: SSE streams text, not tool calls. If you need to show tool progress, send custom events with `event: tool_call`.
