---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Cloud Run Deployment

## Concept

Cloud Run is the serverless option: deploy your agent as a container, pay only for requests, scale to zero when idle. Best for low-to-medium traffic or bursty workloads.

## Setup

```bash
# Build and push
gcloud builds submit --tag gcr.io/my-project/adk-agent

# Deploy
gcloud run deploy adk-agent \
    --image gcr.io/my-project/adk-agent \
    --platform managed \
    --region us-central1 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --concurrency 80 \
    --timeout 300 \
    --set-env-vars GOOGLE_API_KEY=$(gcloud secrets versions access latest --secret=google-api-key) \
    --allow-unauthenticated
```

## FastAPI App for Cloud Run

```python
# main.py
from fastapi import FastAPI, Request
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import SessionService, RedisSessionService
import os

app = FastAPI()
session_service = RedisSessionService(os.environ["REDIS_URL"])
runner = Runner(agent=my_agent, session_service=session_service)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/ready")
async def ready():
    # Check Redis connectivity before reporting ready
    try:
        session_service.ping()
        return {"status": "ready"}
    except:
        return {"status": "not_ready"}, 503

@app.post("/chat/{user_id}")
async def chat(user_id: str, request: Request):
    body = await request.json()
    session = session_service.create_session("chat", user_id)

    async def stream():
        for event in runner.run(body["message"], session=session):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        yield f"data: {part.text}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
```

## Cloud Run vs Vertex AI Agent Engine

| | Cloud Run | Vertex AI Agent Engine |
|---|---|---|
| **Cold start** | 1-3s (with min-instances) | 30-60s |
| **Scale to zero** | Yes | No |
| **Max request time** | 60 min | Unlimited |
| **Model flexibility** | Any (LiteLLM) | Gemini only |
| **Streaming** | Yes (SSE, WebSocket) | Limited |
| **Ops burden** | Medium | Low |

## Pitfalls

- **Cold starts**: First request after idle → 1-3s delay. Set `min-instances=1` for latency-sensitive apps ($30/month minimum).
- **Request timeout**: Cloud Run has a 60-minute max. For agents that need longer, split into async tasks or use Vertex AI.
- **WebSocket support**: Cloud Run has limited WebSocket support. For bidirectional streaming (Live API), use GKE or direct WebSocket connections.
