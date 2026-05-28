---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Async Tools

## Concept

When tools call external APIs, databases, or other slow resources, synchronous execution blocks the agent loop. Async tools let the agent handle multiple tool calls concurrently and make progress while waiting for I/O.

## The Problem With Sync Tools

```python
# Blocking: agent waits 3s before responding
def slow_tool(query: str) -> str:
    time.sleep(3)  # Entire agent loop is stuck
    return fetch_data(query)  # Another 2s
```

## Async Tool Pattern

```python
import asyncio
from google.adk.tools import FunctionTool

async def fetch_product_price(sku: str) -> dict:
    """Fetch current price for a product SKU.

    Args:
        sku: Product SKU code.
    """
    await asyncio.sleep(0.5)  # Simulates network I/O
    return {"sku": sku, "price": 249000, "currency": "IDR"}

async def check_inventory(sku: str) -> dict:
    """Check warehouse inventory for a SKU.

    Args:
        sku: Product SKU code.
    """
    await asyncio.sleep(0.3)
    return {"sku": sku, "stock": 42, "warehouse": "Jakarta"}

agent = Agent(
    name="inventory-agent",
    model="gemini-2.5-flash",
    tools=[
        FunctionTool(fetch_product_price),
        FunctionTool(check_inventory),
    ],
)
```

## Parallel Tool Execution

```python
# These execute concurrently when the LLM calls both in one turn
# Total time: ~0.5s (max of both) instead of 0.8s (sum)
# LLM calls: fetch_product_price("SKU-123") + check_inventory("SKU-123")
```

## Sync-to-Async Bridge

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

def legacy_sync_tool(filepath: str) -> str:
    """Process a file (sync, CPU-bound)."""
    with open(filepath) as f:
        return f.read()

async def async_wrapper(filepath: str) -> str:
    """Async wrapper for legacy sync tool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, legacy_sync_tool, filepath)
```

## Pitfalls

- **Not all tools benefit from async**: CPU-bound tools (data processing, local computation) gain nothing. Only I/O-bound tools (API calls, DB queries) benefit.
- **Thread pool exhaustion**: `run_in_executor` uses a limited thread pool. If all threads are busy, new calls queue. Monitor thread pool usage.
- **Session state is not thread-safe**: If multiple async tools modify `session.state`, you need locking. Prefer returning results and letting the agent compose them.
- **Async at scale**: Each async tool call creates a coroutine. For 100+ concurrent tool calls, use semaphores to limit concurrency.
