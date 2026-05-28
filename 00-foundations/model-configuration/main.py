"""Model Configuration — runnable example.
Tests different model configurations.
Run: python 00-foundations/model-configuration/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def main():
    print("Model Configuration Demo\n")

    configs = [
        ("gemini-2.5-flash", "Flash (fast/cheap)"),
    ]

    for model, label in configs:
        print(f"--- Model: {label} ({model}) ---")

        agent = Agent(
            name=f"model-test-{model}",
            model=model,
            instruction="You are a helpful assistant. Answer in 1 sentence.",
        )

        runner = Runner(agent=agent, session_service=InMemorySessionService())
        session = runner.session_service.create_session("model-test", "user-1")

        print("User: What is the speed of light?")
        print("Agent: ", end="", flush=True)
        for event in runner.run(
            user_input="What is the speed of light?",
            session=session,
        ):
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
