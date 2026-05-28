---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Streaming Tool Results

## Concept

When a tool takes 30 seconds to run, the user sees nothing. Streaming tool results shows progressive output — the user watches the agent work, not wait.

## Generator-Based Tools

```python
from google.adk.tools import FunctionTool
import time

def search_database(query: str) -> str:
    """Search the product database. Returns results progressively."""
    results = db_search(query)  # 5-30 seconds

    # Stream partial results as they arrive
    for result in results:
        yield f"Found: {result['name']} — {result['price']}\n"
        time.sleep(0.1)  # Small delay so user can read

    yield f"\nTotal: {len(results)} results."

agent = Agent(
    name="search-agent",
    model="gemini-2.5-flash",
    tools=[FunctionTool(search_database)],
)
```

## Progress Callbacks

```python
from typing import Callable

def long_running_tool(
    query: str,
    on_progress: Callable[[str], None] = None,
) -> dict:
    """Process large dataset with progress updates."""

    def report(msg: str):
        if on_progress:
            on_progress(msg)

    report("Loading data...")
    data = load_data(query)  # 5s
    report(f"Loaded {len(data)} records. Processing...")

    results = []
    for i, record in enumerate(data):
        results.append(process(record))
        if i % 100 == 0:
            report(f"Processed {i}/{len(data)} records ({i/len(data):.0%})")

    report("Done.")
    return {"count": len(results), "summary": summarize(results)}
```

## Frontend Display

```python
@app.post("/search")
async def search(request: dict):
    async def stream():
        progress = []
        result = await long_running_tool(
            request["query"],
            on_progress=lambda msg: progress.append(msg),
        )
        for p in progress:
            yield f"data: {json.dumps({'progress': p})}\n\n"
        yield f"data: {json.dumps({'result': result})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
```

## Pitfalls

- **Not all tools support streaming**: Third-party APIs may not support progressive responses. Wrap them in polling loops.
- **Stream ordering**: If multiple tools run in parallel, their progress messages interleave. Include tool name in each progress event.
- **Tool output vs model output**: The LLM may wait for full tool output before generating its response. Streaming tool progress helps UX but doesn't speed up the agent loop.
