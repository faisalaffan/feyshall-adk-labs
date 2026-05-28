"""Parallel Agents (Fan-Out/Fan-In) — runnable example.
Run: python 02-multi-agent/parallel-agents/main.py
"""
import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def run_agent_sync(agent, user_input: str) -> str:
    """Run agent in a thread (no async equivalent in ADK)."""
    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session(agent.name, "parallel")
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


async def parallel_analyze(text: str):
    """Run 3 analysis agents concurrently using thread pool."""
    sentiment_agent = Agent(
        name="sentiment",
        model="gemini-2.5-flash",
        instruction="Analyze sentiment. Return JSON: {'sentiment': 'positive'|'negative'|'neutral', 'score': -1.0 to 1.0}.",
    )
    entities_agent = Agent(
        name="entities",
        model="gemini-2.5-flash",
        instruction="Extract named entities (people, companies, locations). Return JSON array.",
    )
    topics_agent = Agent(
        name="topics",
        model="gemini-2.5-flash",
        instruction="Identify 1-3 topics. Return JSON array of strings.",
    )

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=3) as pool:
        sentiment_future = loop.run_in_executor(pool, run_agent_sync, sentiment_agent, text)
        entities_future = loop.run_in_executor(pool, run_agent_sync, entities_agent, text)
        topics_future = loop.run_in_executor(pool, run_agent_sync, topics_agent, text)

        sentiment, entities, topics = await asyncio.gather(
            sentiment_future, entities_future, topics_future
        )

    return {
        "sentiment": sentiment.strip(),
        "entities": entities.strip(),
        "topics": topics.strip(),
    }


def main():
    text = "GoPay just launched a new QR payment feature in Jakarta. Users love the speed but complain about the 0.5% fee."

    print("Parallel Agents Demo (Fan-Out / Fan-In)")
    print(f"Input: {text}\n")

    start = time.monotonic()
    results = asyncio.run(parallel_analyze(text))
    elapsed = time.monotonic() - start

    for agent_name, result in results.items():
        print(f"--- {agent_name.upper()} ---")
        print(result)
        print()

    print(f"All 3 agents completed in {elapsed:.1f}s (ran in parallel)")
    print("Sequential would take ~3x longer.")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
