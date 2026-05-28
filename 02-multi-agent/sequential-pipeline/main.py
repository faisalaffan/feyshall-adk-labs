"""Sequential Pipeline — runnable example.
Run: python 02-multi-agent/sequential-pipeline/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def run_agent(agent, user_input: str, runner: Runner, user_id: str) -> str:
    """Helper: run a single agent and return its text output."""
    session = runner.session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


def main():
    # Agent A: Extract structured data
    extractor = Agent(
        name="extractor",
        model="gemini-2.5-flash",
        instruction="Extract person name, company, and role. Return as JSON only.",
    )

    # Agent B: Analyze the extracted data
    analyzer = Agent(
        name="analyzer",
        model="gemini-2.5-flash",
        instruction="Given JSON with name/company/role, assess if they are a decision-maker. Return JSON: {'decision_maker': true/false, 'confidence': 0-1}.",
    )

    # Agent C: Format for CRM
    formatter = Agent(
        name="formatter",
        model="gemini-2.5-flash",
        instruction="Format the analysis into a one-line CRM summary.",
    )

    runner = Runner(agent=extractor, session_service=InMemorySessionService())

    user_input = "Faisal Affan is CTO at GoPay Indonesia"

    print(f"User: {user_input}\n")
    print("--- Stage 1: Extract ---")
    extracted = run_agent(extractor, user_input, runner, "pipeline")
    print(extracted)

    print("\n--- Stage 2: Analyze ---")
    analyzed = run_agent(analyzer, extracted, runner, "pipeline")
    print(analyzed)

    print("\n--- Stage 3: Format ---")
    formatted = run_agent(formatter, analyzed, runner, "pipeline")
    print(f"CRM Entry: {formatted}")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
