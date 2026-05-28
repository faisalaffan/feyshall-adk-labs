---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Alerting on Agent Behavior

## Concept

Traditional alerts cover infrastructure (CPU, memory, error rate). Agent-specific alerts catch behavioral anomalies: loops, drift, hallucinations, and cost explosions.

## Anomaly Categories

| Category | Signal | Severity |
|----------|--------|----------|
| Agent loop | > 10 turns without resolution | Warning → Critical |
| Cost spike | Token usage 3x baseline | Warning |
| Hallucination | Factual correctness drop > 20% | Critical |
| Tool abuse | Same tool called > 50x in session | Critical |
| Silence | Zero responses for > 5 min | Warning |
| Drift | Response length change > 50% week-over-week | Info → Warning |

## Detection Code

```python
class AgentBehaviorMonitor:
    """Detect anomalous agent behavior in near real-time."""

    def __init__(self, window_seconds: int = 300):
        self.window = window_seconds
        self.baselines = self._load_baselines()

    def check_looping(self, session_id: str) -> bool:
        """Alert if agent exceeds N turns without resolution."""
        turns = get_turn_count(session_id, self.window)
        if turns > 10:
            alert(
                severity="warning",
                title=f"Agent looping detected: {session_id}",
                body=f"Session {session_id} has {turns} turns in {self.window}s",
            )
            return True
        return False

    def check_cost_spike(self, agent_name: str) -> bool:
        """Alert if token usage exceeds baseline."""
        current = get_token_rate(agent_name, window_minutes=10)
        baseline = self.baselines.get(agent_name, {}).get("token_rate", 0)
        if baseline > 0 and current > baseline * 3:
            alert(
                severity="warning",
                title=f"Cost spike: {agent_name}",
                body=f"Token rate: {current}/min (baseline: {baseline}/min)",
            )
            return True
        return False

    def check_hallucination_drift(self, agent_name: str) -> bool:
        """Alert if factual correctness drops below threshold."""
        score = get_factual_correctness(agent_name, window_hours=1)
        baseline = self.baselines.get(agent_name, {}).get("factual", 1.0)
        if score < baseline * 0.8:  # 20% drop
            alert(
                severity="critical",
                title=f"Hallucination drift: {agent_name}",
                body=f"Factual correctness: {score:.1%} (baseline: {baseline:.1%})",
            )
            return True
        return False
```

## Alert Routing

```python
ALERT_ROUTING = {
    "critical": ["pagerduty", "slack#agent-alerts"],
    "warning": ["slack#agent-alerts"],
    "info": ["slack#agent-ops"],
}

def alert(severity: str, title: str, body: str):
    for channel in ALERT_ROUTING.get(severity, []):
        send_alert(channel, title, body)
```

## Pitfalls

- **Alert fatigue**: If every loop triggers a page, on-call ignores alerts. Set thresholds based on actual pain points, not theoretical limits.
- **Baseline drift**: What's "normal" changes as your product grows. Recompute baselines weekly.
- **Correlation ≠ causation**: A cost spike might be a marketing campaign, not a runaway agent. Include context in alerts.
- **Silence detection needs heartbeats**: If your monitoring pipeline goes down, you won't detect silence because there are no metrics to check. Use a separate heartbeat monitor.
