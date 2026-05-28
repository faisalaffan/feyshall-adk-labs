---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Tool With Auth

## Concept

Tools that call external APIs need authentication. Hardcoding credentials is a security risk. This recipe covers patterns for OAuth, API keys, and secret management in ADK tools.

## API Key Pattern

```python
import os
from google.adk.tools import FunctionTool

def send_slack_message(channel: str, text: str) -> str:
    """Send a message to a Slack channel.

    Args:
        channel: Slack channel ID or name.
        text: Message body.
    """
    token = os.environ["SLACK_BOT_TOKEN"]  # Never hardcode
    # ... call Slack API with token
    return f"Message sent to {channel}"
```

## OAuth Pattern

```python
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def gmail_tool(query: str) -> list[dict]:
    """Search Gmail for emails matching a query.

    Args:
        query: Gmail search query (e.g., "from:boss@company.com").
    """
    creds = Credentials(
        token=os.environ["GMAIL_ACCESS_TOKEN"],
        refresh_token=os.environ["GMAIL_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GMAIL_CLIENT_ID"],
        client_secret=os.environ["GMAIL_CLIENT_SECRET"],
    )

    if creds.expired:
        creds.refresh(Request())
        # In production: store refreshed token back to secret manager

    # ... call Gmail API
    return [{"subject": "...", "from": "..."}]
```

## Secret Manager Integration

```python
from google.cloud import secretmanager

class SecretBackedTool:
    """Tool that fetches credentials from GCP Secret Manager at runtime."""

    def __init__(self, project_id: str, secret_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    def get_secret(self) -> str:
        response = self.client.access_secret_version(name=self.secret_path)
        return response.payload.data.decode("UTF-8")

    def api_call(self, endpoint: str, payload: dict) -> dict:
        api_key = self.get_secret()
        # ... make authenticated API call
        return {"status": "ok"}
```

## Auth Strategy Decision Tree

```
Is this a Google API?
├── Yes → Use ADC (Application Default Credentials)
│         gcloud auth application-default login
│
└── No → Is the user the one authenticating?
    ├── Yes → Use OAuth with per-user tokens
    │         Store tokens in session state
    │
    └── No → Use API key from Secret Manager
              Rotate keys every 90 days
```

## Pitfalls

- **Don't put secrets in tool descriptions**: The LLM sees tool descriptions. Never include example API keys in docstrings.
- **Token refresh in long sessions**: OAuth tokens expire. If your agent session spans hours, implement `cred.refresh()` in a tool wrapper.
- **Secret Manager latency**: Fetching secrets at tool invocation adds 50-200ms. For latency-sensitive tools, cache credentials with a TTL.
- **Session state is NOT a secret store**: Don't store raw API keys in ADK session state. Sessions can be serialized to disk.
