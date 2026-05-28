"""Regression test suite for agent behavior.

Run with: python -m pytest tests/eval/test_regression.py -v
"""
import pytest

REGRESSION_CASES = [
    # (input, expected_behavior_description)
    ("Hello", "agent_greets_politely"),
    ("What can you do?", "agent_lists_capabilities"),
    ("Tell me a joke", "agent_tells_joke_or_refuses_appropriately"),
    ("What is 2+2?", "agent_answers_4"),
    ("Goodbye", "agent_says_goodbye"),
    # Edge cases
    ("", "empty_input_handled"),
    ("   ", "whitespace_only_handled"),
    ("a" * 1000, "very_long_input_handled"),
    ("!@#$%^&*()", "special_chars_handled"),
]


@pytest.mark.parametrize("user_input,test_id", REGRESSION_CASES)
def test_regression_basic_behavior(user_input, test_id):
    """Agent must not crash or return empty on common inputs."""
    import os

    if not os.environ.get("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")

    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    agent = Agent(
        name="regression-test-agent",
        model="gemini-2.5-flash",
        instruction="You are a helpful assistant. Be concise.",
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("regression", "user-1")

    output = []
    try:
        for event in runner.run(user_input=user_input, session=session):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        output.append(part.text)
    except Exception as e:
        pytest.fail(f"[{test_id}] Agent crashed on input '{user_input[:50]}': {e}")

    response = "".join(output).strip()
    assert len(response) > 0, f"[{test_id}] Agent returned empty response"
    assert len(response) < 10000, f"[{test_id}] Agent returned excessively long response ({len(response)} chars)"
