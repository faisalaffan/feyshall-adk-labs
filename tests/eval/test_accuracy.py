"""Accuracy evaluation suite for ADK agents.

Run with: python -m pytest tests/eval/test_accuracy.py -v
"""
import pytest

# Accuracy regression cases
ACCURACY_CASES = [
    (
        "What is the capital of Indonesia?",
        ["jakarta"],
        ["surabaya", "bandung", "medan"],
        "factual_capital",
    ),
    (
        "Convert 100 Celsius to Fahrenheit",
        ["212"],
        [],
        "simple_conversion",
    ),
    (
        "List three primary colors",
        ["red", "blue", "yellow"],
        [],
        "common_knowledge",
    ),
    (
        "What is 15 * 27?",
        ["405"],
        [],
        "multiplication",
    ),
    (
        "Is water H2O or CO2?",
        ["h2o"],
        ["co2"],
        "basic_science",
    ),
]


@pytest.mark.parametrize("user_input,must_contain,must_not,test_id", ACCURACY_CASES)
def test_accuracy(user_input, must_contain, must_not, test_id):
    """Agent must return factually correct responses."""
    import os

    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set — skipping LLM-dependent accuracy test")

    from google.adk.agents import Agent

    agent = Agent(
        name="accuracy-test-agent",
        model="gemini-2.5-flash",
        instruction="Answer questions accurately and concisely. Just give the answer, no explanation.",
    )

    response = run_agent(agent, user_input).lower()

    for phrase in must_contain:
        assert phrase.lower() in response, (
            f"[{test_id}] Missing '{phrase}' in response: {response[:200]}"
        )

    for phrase in must_not:
        assert phrase.lower() not in response, (
            f"[{test_id}] Found forbidden '{phrase}' in response: {response[:200]}"
        )


def run_agent(agent, user_input: str) -> str:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("test", "user-1")
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)
