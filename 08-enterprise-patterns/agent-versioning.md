---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Agent Versioning

## Concept

As agents evolve, you need to deploy new versions without breaking existing users. Canary deployments, versioned endpoints, and A/B testing let you ship safely.

## Version Strategy

```
agents/
├── customer-support/
│   ├── v1/
│   │   ├── agent.py       ← Stable, serving 95% traffic
│   │   └── instruction.txt
│   ├── v2/
│   │   ├── agent.py       ← Canary, serving 5% traffic
│   │   └── instruction.txt
│   └── canary_config.yaml
```

## Version Registry

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentVersion:
    version: str          # "v1", "v2", "canary"
    agent: Agent
    traffic_pct: float    # 0.0 to 1.0
    min_turns: int        # Minimum turns before version locks in

class VersionedAgentRouter:
    """Routes requests to agent versions based on traffic split."""

    def __init__(self, versions: list[AgentVersion]):
        self.versions = versions
        self._validate_split()

    def _validate_split(self):
        total = sum(v.traffic_pct for v in self.versions)
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Traffic split must sum to 1.0, got {total}")

    def route(self, session_id: str) -> AgentVersion:
        """Deterministic routing: same session always gets the same version."""
        # Hash session_id to pick a version consistently
        bucket = hash(session_id) % 100 / 100.0
        cumulative = 0
        for version in self.versions:
            cumulative += version.traffic_pct
            if bucket <= cumulative:
                return version
        return self.versions[-1]  # Fallback to last

# Usage
router = VersionedAgentRouter([
    AgentVersion("v1", customer_support_v1, traffic_pct=0.90),
    AgentVersion("v2", customer_support_v2, traffic_pct=0.10),
])

def handle_request(session_id, user_input):
    version = router.route(session_id)
    print(f"Routing to {version.version}")
    return run_agent(version.agent, user_input)
```

## Canary Promotion Checklist

1. Deploy v2 with 1% traffic
2. Monitor error rate, latency, user satisfaction for 1 hour
3. If metrics are healthy → 10% → 50% → 100%
4. If metrics degrade → auto-rollback to v1
5. Once at 100%, archive v1 after 7 days

## Pitfalls

- **Session stickiness**: A user on v1 must stay on v1 for the session duration. Switching versions mid-conversation breaks context.
- **Tool compatibility**: v2 might use different tool signatures. If both versions share a tool backend, the tool must be backward-compatible.
- **Eval comparison**: Run both versions against the same eval set before promoting. A 2% improvement on evals might hide a 10% regression on real traffic.
- **Config drift**: If you version agents but not their configuration (model, temperature, tools), you're not truly versioning. Pin everything.
