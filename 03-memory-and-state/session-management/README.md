---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Session Management

## Concept

ADK sessions store conversation history and agent state across turns. `InMemorySessionService` works for development; production needs persistent backends.

## In-Memory (Dev)

```python
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()
session = session_service.create_session(
    app_name="my-app",
    user_id="user-1",
)

# All conversation state lives in memory
# Restart = all sessions lost
```

## Persistent Session (File-Based)

```python
import json
import os
from google.adk.sessions import SessionService

class FileSessionService(SessionService):
    """Persist sessions to disk. For single-instance deployments."""

    def __init__(self, base_path: str = "./sessions"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def create_session(self, app_name: str, user_id: str) -> str:
        session_id = f"{app_name}:{user_id}"
        path = self._path(session_id)
        if not os.path.exists(path):
            self._write(session_id, {"history": [], "state": {}})
        return session_id

    def _path(self, session_id: str) -> str:
        return os.path.join(self.base_path, f"{session_id}.json")

    def _read(self, session_id: str) -> dict:
        with open(self._path(session_id)) as f:
            return json.load(f)

    def _write(self, session_id: str, data: dict):
        with open(self._path(session_id), "w") as f:
            json.dump(data, f, indent=2)
```

## Session Lifecycle

```
create → active → (TTL expires) → expired → (cleanup) → deleted
  │                   │
  │                   └── On each request: extend TTL
  └── First user message: allocate session
```

## Pitfalls

- **In-memory sessions don't survive restart**: Use only for local dev. Tests pass, production breaks.
- **Session ID guessing**: Don't use sequential IDs (`session-1`, `session-2`). Use UUIDs.
- **No built-in TTL**: ADK sessions live forever by default. Implement a cleanup job for expired sessions.
- **Session size grows unbounded**: Long conversations hit context limits. See `context-compaction.md`.
