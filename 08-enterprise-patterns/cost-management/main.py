"""Cost Management — token budgets, model tier selection, cost tracking.
Run: python 08-enterprise-patterns/cost-management/main.py
"""
from dataclasses import dataclass, field
from datetime import datetime


MODEL_TIERS = {
    "critical": {"model": "gemini-2.5-pro", "cost_1k_in": 0.00125, "cost_1k_out": 0.005},
    "default": {"model": "gemini-2.5-flash", "cost_1k_in": 0.00015, "cost_1k_out": 0.0006},
    "budget": {"model": "gemini-2.5-flash-lite", "cost_1k_in": 0.000075, "cost_1k_out": 0.0003},
}


def select_model(intent: str, user_tier: str) -> dict:
    """Select model tier based on task importance and user plan."""
    if user_tier == "enterprise" and intent in ("financial", "medical", "legal"):
        return MODEL_TIERS["critical"]
    if user_tier == "free":
        return MODEL_TIERS["budget"]
    return MODEL_TIERS["default"]


def calculate_cost(model_tier: str, input_tokens: int, output_tokens: int) -> float:
    tier = MODEL_TIERS[model_tier]
    return round(
        input_tokens / 1000 * tier["cost_1k_in"]
        + output_tokens / 1000 * tier["cost_1k_out"],
        6,
    )


@dataclass
class CostTracker:
    records: list = field(default_factory=list)

    def record(self, agent_name: str, user_id: str, model_tier: str,
               input_tokens: int, output_tokens: int):
        cost = calculate_cost(model_tier, input_tokens, output_tokens)
        self.records.append({
            "time": datetime.now().isoformat(),
            "agent": agent_name,
            "user": user_id,
            "model": MODEL_TIERS[model_tier]["model"],
            "tokens_in": input_tokens,
            "tokens_out": output_tokens,
            "cost_usd": cost,
        })
        return cost

    def daily_total(self, user_id: str) -> float:
        return sum(r["cost_usd"] for r in self.records if r["user"] == user_id)


def main():
    print("Cost Management Demo\n")

    # Model selection
    test_cases = [
        ("financial", "enterprise"),
        ("general", "enterprise"),
        ("general", "free"),
        ("medical", "free"),
    ]
    print("--- Model Selection ---")
    for intent, tier in test_cases:
        model = select_model(intent, tier)
        print(f"  {intent:12} | {tier:10} → {model['model']:25} "
              f"(${model['cost_1k_in']}/1K in)")

    # Cost tracking
    print("\n--- Cost Tracking ---")
    tracker = CostTracker()

    scenarios = [
        ("faq-agent", "user-1", "default", 500, 200),
        ("faq-agent", "user-1", "default", 300, 150),
        ("financial-agent", "user-2", "critical", 2000, 800),
        ("faq-agent", "user-3", "budget", 400, 100),
    ]

    for agent, user, tier, inp, out in scenarios:
        cost = tracker.record(agent, user, tier, inp, out)
        model_name = MODEL_TIERS[tier]["model"]
        print(f"  {user} → {agent} ({model_name}): {inp}+{out} tokens = ${cost:.6f}")

    print(f"\n  Daily total (user-1): ${tracker.daily_total('user-1'):.6f}")
    print(f"  Daily total (user-2): ${tracker.daily_total('user-2'):.6f}")
    print(f"  Daily total (user-3): ${tracker.daily_total('user-3'):.6f}")

    # Comparison
    print("\n--- Cost Comparison (1000 req × 500 in + 200 out tokens) ---")
    for tier_name, tier in MODEL_TIERS.items():
        cost = calculate_cost(tier_name, 500 * 1000, 200 * 1000)
        print(f"  {tier_name:10} ({tier['model']:25}): ${cost:.2f}/day")


if __name__ == "__main__":
    main()
