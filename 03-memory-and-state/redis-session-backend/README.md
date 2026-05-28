---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Redis Session Backend

## Concept

For multi-instance deployments, sessions must be shared across server instances. Redis provides fast, atomic session storage with built-in TTL and pub/sub for real-time updates.

## Architecture

```
Instance A ──┐
             ├──► Redis ◄── Session data
Instance B ──┘     │
                   ├── Session hash: {session_id: json_blob}
                   ├── TTL: EXPIRE session_id 3600
                   └── Pub/Sub: session_updates channel
```

## Code

```python
import json
import redis
import uuid
from google.adk.sessions import SessionService

class RedisSessionService(SessionService):
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 3600):
        self.redis = redis.from_url(redis_url)
        self.ttl = ttl

    def create_session(self, app_name: str, user_id: str) -> str:
        session_id = f"{app_name}:{user_id}:{uuid.uuid4().hex[:8]}"
        self.redis.setex(
            session_id,
            self.ttl,
            json.dumps({"history": [], "state": {}, "created_at": time.time()}),
        )
        return session_id

    def get_session(self, session_id: str) -> dict:
        data = self.redis.get(session_id)
        if not data:
            raise SessionNotFoundError(session_id)
        # Extend TTL on access
        self.redis.expire(session_id, self.ttl)
        return json.loads(data)

    def update_session(self, session_id: str, data: dict):
        self.redis.setex(session_id, self.ttl, json.dumps(data))
        # Notify other instances
        self.redis.publish("session_updates", json.dumps({
            "session_id": session_id,
            "timestamp": time.time(),
        }))

    def delete_session(self, session_id: str):
        self.redis.delete(session_id)
```

## Production Hardening

```python
# Connection pooling + retry
redis_pool = redis.ConnectionPool(
    host="redis-prod.internal",
    port=6379,
    max_connections=50,
    retry_on_timeout=True,
    health_check_interval=30,
)

# Sentinel for high availability
from redis.sentinel import Sentinel
sentinel = Sentinel([("sentinel-1", 26379), ("sentinel-2", 26379)])
redis_client = sentinel.master_for("adk-sessions")
```

## Pitfalls

- **Redis memory cap**: Sessions can grow large. Set `maxmemory` and an eviction policy (`volatile-lru`).
- **Serialization overhead**: JSON serialization of full session state on every request adds 5-20ms. Consider msgpack for high-throughput.
- **Redis is not durable by default**: Enable AOF persistence. Losing Redis = losing all active conversations.
- **No cross-region replication**: Redis sessions are region-bound. Multi-region deployments need a different approach (DynamoDB, Spanner).
