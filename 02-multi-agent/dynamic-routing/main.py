"""Dynamic Routing — LLM-driven vs rule-based routing.
Run: python 02-multi-agent/dynamic-routing/main.py
"""
import os
import re
import time
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent(agent, user_input: str, user_id: str = "routing") -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


# Routing rules (regex-based, fast path)
ROUTING_RULES = [
    (r"(?i)(invoice|payment|refund|charge|billing)", "billing"),
    (r"(?i)(bug|error|crash|500|timeout|api|broken)", "technical"),
    (r"(?i)(login|password|profile|sign.*in|account)", "account"),
]


def rule_route(user_input: str) -> str:
    """Regex-based routing. ~1ms, no LLM cost."""
    for pattern, category in ROUTING_RULES:
        if re.search(pattern, user_input):
            return category
    return "general"


# LLM router (slow path, fallback)
router_agent = Agent(
    name="router",
    model="gemini-2.5-flash",
    instruction="""Classify user input into EXACTLY ONE category:
    - 'billing' — payment, invoice, refund
    - 'technical' — bugs, errors, API
    - 'account' — login, password, profile
    - 'general' — everything else
    Return ONLY the category name, nothing else. No explanation.""",
)


def llm_route(user_input: str) -> str:
    """LLM-based routing. ~500ms-2s, more accurate."""
    return run_agent(router_agent, user_input, "router").strip().lower()


def hybrid_route(user_input: str) -> tuple[str, str]:
    """Rule-based first (fast), LLM fallback (accurate)."""
    rule_result = rule_route(user_input)
    if rule_result != "general":
        return rule_result, "rule"
    llm_result = llm_route(user_input)
    return llm_result, "llm"


def main():
    test_queries = [
        "My invoice #12345 hasn't been paid",
        "The API is returning 500 errors after the last deploy",
        "I can't log into my account, forgot password",
        "Do you have vegan options on the menu?",
    ]

    print("Dynamic Routing Demo\n")
    print(f"{'Query':<55} {'Route':<12} {'Method':<8} {'Time'}")
    print("-" * 85)

    for query in test_queries:
        start = time.monotonic()
        route, method = hybrid_route(query)
        elapsed = (time.monotonic() - start) * 1000

        query_short = query[:52] + ("..." if len(query) > 52 else "")
        print(f"{query_short:<55} {route:<12} {method:<8} {elapsed:.0f}ms")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
