---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Audit Logging

## Concept

Every agent action — tool calls, user inputs, model decisions — must be logged immutably for compliance, debugging, and security forensics. This is non-negotiable in regulated industries.

## What to Log

```python
import json
import time
import hashlib
from dataclasses import dataclass, asdict

@dataclass
class AuditEvent:
    timestamp: str
    event_type: str  # 'user_input', 'tool_call', 'tool_result', 'llm_response', 'error'
    agent_name: str
    session_id: str
    user_id: str
    tenant_id: str
    data: dict
    event_hash: str  # For tamper detection

    @classmethod
    def create(cls, event_type, agent_name, session_id, user_id, tenant_id, data):
        event = cls(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            event_type=event_type,
            agent_name=agent_name,
            session_id=session_id,
            user_id=user_id,
            tenant_id=tenant_id,
            data=data,
            event_hash="",
        )
        # Hash the event for tamper detection
        raw = json.dumps(asdict(event), sort_keys=True, default=str)
        event.event_hash = hashlib.sha256(raw.encode()).hexdigest()
        return event
```

## Immutable Log Store

```python
import logging
from google.cloud import bigquery

class AuditLogger:
    """Writes to both structured logs (BigQuery) and append-only file."""

    def __init__(self, bigquery_table: str):
        self.bq_table = bigquery_table
        self.file_logger = logging.getLogger("audit")
        # File logger writes to append-only storage (GCS, S3 with object lock)

    def log(self, event: AuditEvent):
        # Async write to BigQuery for querying
        self._write_bigquery(event)
        # Sync write to append-only log for compliance
        self.file_logger.info(json.dumps(asdict(event), default=str))

    def _write_bigquery(self, event: AuditEvent):
        # Batch insert for production; single insert for clarity
        client = bigquery.Client()
        rows = [asdict(event)]
        client.insert_rows_json(self.bq_table, rows)
```

## What NOT to Log

```
# NEVER log these
- API keys, tokens, secrets
- Full credit card numbers (mask to last 4)
- Passwords or auth tokens
- PII without hashing (emails, phone numbers, addresses)
- Full conversation history (log hashes, not raw text, for PII)
```

## Audit Checklist

- [ ] Every tool call is logged (input params + result signature)
- [ ] Every user input is logged (hash for PII-sensitive contexts)
- [ ] Logs are append-only and immutable (object lock, WORM storage)
- [ ] Log retention matches compliance requirements (SOC2: 90d, HIPAA: 6y)
- [ ] Log tampering is detectable (hash chain or signing)

## Pitfalls

- **Log volume**: An agent making 5 tool calls per user turn generates 15+ audit events. At 10k users/day, that's 150k events. Budget for BigQuery or equivalent.
- **PII in tool results**: A tool that returns customer data may leak PII into logs. Sanitize tool results before logging.
- **Log injection**: If you log raw user input, a malicious user can inject newlines or JSON to fake log entries. Sanitize or use structured logging.
