"""Centralized configuration for ADK agent runtime."""
import os
from dataclasses import dataclass, field


@dataclass
class AgentConfig:
    environment: str
    model: str
    temperature: float
    max_turns: int
    redis_url: str = ""
    otel_endpoint: str = ""
    log_level: str = "info"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        env = os.getenv("APP_ENV", "dev")

        defaults = {
            "dev": dict(
                environment="dev",
                model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
                temperature=0.7,
                max_turns=15,
                log_level="debug",
            ),
            "staging": dict(
                environment="staging",
                model=os.getenv("AGENT_MODEL", "gemini-2.5-flash"),
                temperature=0.3,
                max_turns=10,
                log_level="info",
            ),
            "prod": dict(
                environment="prod",
                model=os.getenv("AGENT_MODEL", "gemini-2.5-pro"),
                temperature=0.1,
                max_turns=5,
                log_level="warning",
            ),
        }

        cfg = defaults.get(env, defaults["dev"])
        cfg["redis_url"] = os.getenv("REDIS_URL", "")
        cfg["otel_endpoint"] = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        return cls(**cfg)
