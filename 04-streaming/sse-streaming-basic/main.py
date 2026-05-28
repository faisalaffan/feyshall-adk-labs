"""SSE Streaming — runnable FastAPI server.
Run: uvicorn 04-streaming.sse-streaming-basic.main:app --port 8000
"""
import os
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def get_server_time() -> str:
    """Get the current server time."""
    import time
    return time.strftime("%H:%M:%S %Z", time.localtime())


agent = Agent(
    name="streaming-demo",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Keep responses brief.",
    tools=[FunctionTool(get_server_time)],
)

runner = Runner(agent=agent, session_service=InMemorySessionService())

app = FastAPI(title="SSE Streaming Demo")


@app.post("/chat/{user_id}")
async def chat(user_id: str, request: dict):
    session = runner.session_service.create_session("chat", user_id)

    async def stream():
        for event in runner.run(
            user_input=request.get("message", ""),
            session=session,
        ):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {json.dumps({'text': part.text})}\n\n"
                    if hasattr(part, "tool_call") and part.tool_call:
                        yield f"data: {json.dumps({'tool': part.tool_call.name})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
