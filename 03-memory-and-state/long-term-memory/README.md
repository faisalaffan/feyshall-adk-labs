---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Long-Term Memory

## Concept

Agents forget everything between sessions by default. Long-term memory stores facts, preferences, and learnings across conversations using vector databases.

## Architecture

```
User: "I prefer email summaries on Fridays"
        │
        ▼
    Agent stores → Vector DB (embedding)
                         │
User (next week): "Send my summary"  │
        │                           │
        ▼                           ▼
    Agent retrieves → "User prefers Friday email summaries"
```

## Code (Qdrant)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class LongTermMemory:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self.embedder = Embedder()  # text-embedding-004 or similar
        self._ensure_collection()

    def _ensure_collection(self):
        self.client.create_collection(
            collection_name="agent_memory",
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    def store(self, user_id: str, fact: str, metadata: dict = None):
        """Store a fact about the user."""
        embedding = self.embedder.embed(fact)
        self.client.upsert(
            collection_name="agent_memory",
            points=[PointStruct(
                id=hash(fact),
                vector=embedding,
                payload={
                    "user_id": user_id,
                    "fact": fact,
                    "metadata": metadata or {},
                    "stored_at": time.time(),
                },
            )],
        )

    def recall(self, user_id: str, query: str, top_k: int = 5) -> list[str]:
        """Recall relevant facts about the user."""
        embedding = self.embedder.embed(query)
        results = self.client.search(
            collection_name="agent_memory",
            query_vector=embedding,
            query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
            limit=top_k,
        )
        return [r.payload["fact"] for r in results]

    def forget(self, user_id: str, fact_pattern: str):
        """Delete facts matching a pattern."""
        self.client.delete(
            collection_name="agent_memory",
            points_selector={"filter": {
                "must": [
                    {"key": "user_id", "match": {"value": user_id}},
                ],
            }},
        )
```

## Memory Types

| Type | Storage | Retrieval | Example |
|------|---------|-----------|---------|
| Facts | Vector DB | Semantic search | "User is vegetarian" |
| Preferences | Vector DB | Semantic search | "Prefers bullet points" |
| Episodes | Vector DB | Time + semantic | "Last week's meeting notes" |
| Skills | Code/config | Direct lookup | Tool definitions |

## Pitfalls

- **Memory pollution**: Old, conflicting facts accumulate. Implement memory expiry and conflict resolution.
- **Embedding cost**: Every `store()` and `recall()` costs an embedding API call. Batch stores, cache frequent recalls.
- **Privacy**: Stored facts may contain PII. Encrypt at rest and implement right-to-delete.
- **Relevance decay**: A fact from 6 months ago may be less relevant than one from yesterday. Weight by recency.
