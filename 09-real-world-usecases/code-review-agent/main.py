"""Code Review Agent — runnable example.
Reviews a code snippet using 3 parallel reviewer agents.
Run: python 09-real-world-usecases/code-review-agent/main.py
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()

SAMPLE_CODE = '''
def process_payment(amount, user_id):
    import pickle
    data = pickle.loads(user_id)  # unsafe
    api_key = "sk-abc123xyz"  # hardcoded
    result = db.execute("SELECT * FROM payments WHERE id = " + user_id)
    for i in range(len(result)):
        for j in range(len(result)):
            print(i, j)
    return result
'''


def run_agent_sync(agent, user_input: str) -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, "review")
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


async def review_parallel(code: str):
    style_agent = Agent(
        name="style-reviewer",
        model="gemini-2.5-flash",
        instruction="Review code for style: naming, type hints, function length. List issues only.",
    )
    security_agent = Agent(
        name="security-reviewer",
        model="gemini-2.5-flash",
        instruction="Review code for security: hardcoded keys, injection, unsafe deserialization. List issues only.",
    )
    logic_agent = Agent(
        name="logic-reviewer",
        model="gemini-2.5-flash",
        instruction="Review code for logic: bugs, edge cases, O(n²), resource leaks. List issues only.",
    )

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = await asyncio.gather(
            loop.run_in_executor(pool, run_agent_sync, style_agent, f"Review:\n{code}"),
            loop.run_in_executor(pool, run_agent_sync, security_agent, f"Review:\n{code}"),
            loop.run_in_executor(pool, run_agent_sync, logic_agent, f"Review:\n{code}"),
        )

    return {"style": results[0], "security": results[1], "logic": results[2]}


def main():
    print("Code Review Agent Demo\n")
    print("--- Code to Review ---")
    print(SAMPLE_CODE)

    print("\n--- Review Results (3 parallel agents) ---")
    results = asyncio.run(review_parallel(SAMPLE_CODE))

    for category, feedback in results.items():
        print(f"\n## {category.upper()}")
        print(feedback)


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
