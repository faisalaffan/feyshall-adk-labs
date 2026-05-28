---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Environment Config Management

## Concept

Agents run in different environments (dev, staging, prod) with different configs, API keys, and model tiers. Centralize config to avoid drift and secret leaks.

## Config Hierarchy

```python
# config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    environment: str          # dev, staging, prod
    model: str               # gemini-2.5-flash, claude-sonnet-4-6
    temperature: float
    max_turns: int
    redis_url: str
    api_key: Optional[str] = None  # Never log this

    @classmethod
    def from_env(cls) -> "AgentConfig":
        env = os.getenv("APP_ENV", "dev")
        configs = {
            "dev": cls(
                environment="dev",
                model="gemini-2.5-flash",
                temperature=0.7,
                max_turns=15,
                redis_url="redis://localhost:6379",
            ),
            "staging": cls(
                environment="staging",
                model="gemini-2.5-flash",
                temperature=0.3,
                max_turns=10,
                redis_url=os.environ["REDIS_URL"],
            ),
            "prod": cls(
                environment="prod",
                model="gemini-2.5-pro",
                temperature=0.1,
                max_turns=5,
                redis_url=os.environ["REDIS_URL"],
            ),
        }
        config = configs[env]
        config.api_key = _load_api_key()
        return config

def _load_api_key() -> str:
    # Priority: env var > GCP Secret Manager > error
    if key := os.getenv("GOOGLE_API_KEY"):
        return key
    if key := _fetch_from_secret_manager("google-api-key"):
        return key
    raise RuntimeError("No API key configured")
```

## Secrets Management

```python
from google.cloud import secretmanager

def _fetch_from_secret_manager(secret_id: str) -> Optional[str]:
    """Fetch secret from GCP Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{os.environ['GCP_PROJECT']}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception:
        return None
```

## .env Files for Local Dev

```bash
# .env — NEVER commit this file
GOOGLE_API_KEY=AIza...
APP_ENV=dev
REDIS_URL=redis://localhost:6379

# .env.example — commit this, shows required vars
GOOGLE_API_KEY=your-api-key-here
APP_ENV=dev
REDIS_URL=redis://localhost:6379
```

## Environment-Specific Tool Behavior

```python
def get_weather(city: str) -> dict:
    """In dev, return mock data. In prod, call real API."""
    if os.getenv("APP_ENV") == "dev":
        return {"city": city, "temp": 30, "mock": True}
    return real_weather_api(city)
```

## Pitfalls

- **Config in code**: `if env == "prod": model = "gemini-pro"` scattered across files creates drift. Centralize in one `Config` class.
- **Secrets in config files**: JSON/YAML config files with API keys get committed accidentally. Use env vars or secret manager.
- **Environment parity**: "It works in dev" doesn't mean anything if dev uses flash and prod uses pro. Test with the prod model tier in staging.
