"""
FastAPI entrypoint for ADK agent runtime.
Run: uvicorn main:app --host 0.0.0.0 --port 8000
"""
import os
import json
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from config import AgentConfig

# Load config based on environment
config = AgentConfig.from_env()

# Define tools
def get_current_time() -> str:
    """Get the current server time in ISO format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def health_check() -> dict:
    """Check system health and connectivity."""
    return {
        "status": "ok",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": config.environment,
        "model": config.model,
    }

# Create agent
agent = Agent(
    name="adk-agent",
    model=config.model,
    instruction="You are a helpful AI assistant running on Google ADK.",
    tools=[
        FunctionTool(get_current_time),
        FunctionTool(health_check),
    ],
)

# Initialize runner
runner = Runner(
    agent=agent,
    session_service=InMemorySessionService(),
)

# FastAPI app
app = FastAPI(
    title="ADK Agent Runtime",
    version="1.28",
    docs_url="/docs" if config.environment == "dev" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": config.environment}


@app.get("/ready")
async def ready():
    try:
        # Check core dependencies
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}, 503


@app.post("/chat/{user_id}")
async def chat(user_id: str, request: Request):
    body = await request.json()
    user_input = body.get("message", body.get("input", ""))
    session = runner.session_service.create_session("chat", user_id)

    async def stream():
        for event in runner.run(user_input=user_input, session=session):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {json.dumps({'text': part.text})}\n\n"
                    if hasattr(part, 'tool_call') and part.tool_call:
                        yield f"data: {json.dumps({'tool_call': part.tool_call.name})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/agents/{agent_name}/run")
async def run_agent_sync(agent_name: str, request: Request):
    """Non-streaming agent run."""
    body = await request.json()
    user_input = body.get("input", body.get("message", ""))
    session = runner.session_service.create_session(agent_name, body.get("user_id", "default"))

    output_parts = []
    tool_calls = []

    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output_parts.append(part.text)
                if hasattr(part, 'tool_call') and part.tool_call:
                    tool_calls.append({
                        "name": part.tool_call.name,
                        "args": getattr(part.tool_call, 'args', {}),
                    })

    return {
        "output": "".join(output_parts),
        "tool_calls": tool_calls,
        "session_id": session.session_id,
    }
