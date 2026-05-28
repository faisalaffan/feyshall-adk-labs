"""Frontend Integration — FastAPI backend for Next.js/Flutter streams.
Run: python 04-streaming/frontend-integration/server.py
"""
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def get_weather(city: str) -> dict:
    """Get weather for a city."""
    return {"city": city, "temp_c": 32, "condition": "sunny"}


agent = Agent(
    name="frontend-demo",
    model="gemini-2.5-flash",
    instruction="You are a helpful assistant. Use weather tool when asked about weather.",
    tools=[FunctionTool(get_weather)],
)

runner = Runner(agent=agent, session_service=InMemorySessionService())

app = FastAPI(title="Frontend Integration API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.post("/api/chat")
async def chat(request: dict):
    session = runner.session_service.create_session("frontend", request.get("userId", "anon"))

    async def stream():
        for event in runner.run(
            user_input=request.get("message", ""),
            session=session,
        ):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {json.dumps({'text': part.text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    import uvicorn
    print("Frontend Integration API running on http://localhost:8000")
    print("POST /api/chat with {'message': '...', 'userId': '...'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
