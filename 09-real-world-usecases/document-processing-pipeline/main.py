"""Document Processing Pipeline — runnable example.
Extract text → classify → extract entities → validate.
Run: python 09-real-world-usecases/document-processing-pipeline/main.py
"""
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent_sync(agent, user_input: str) -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, "docs")
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


SAMPLE_INVOICE = """
INVOICE #INV-2026-0501
Date: May 15, 2026
Vendor: PT Teknologi Nusantara
Customer: PT Retail Indonesia
Items:
  - Cloud Infrastructure: Rp 25,000,000
  - AI Consulting (40 hours): Rp 40,000,000
Total: Rp 65,000,000
Due Date: June 15, 2026
Payment Terms: NET-30
"""


def main():
    print("Document Processing Pipeline Demo\n")
    print(f"Input Document:\n{SAMPLE_INVOICE}\n")
    print("=" * 50)

    # Stage 1: Extract
    extract_agent = Agent(
        name="extractor",
        model="gemini-2.5-flash",
        instruction="Extract all text fields from the document. List them as key-value pairs.",
    )
    extracted = run_agent_sync(extract_agent, f"Extract all fields:\n{SAMPLE_INVOICE}")
    print(f"\n[EXTRACT]\n{extracted}")

    # Stage 2: Classify (parallel with entity extraction)
    classify_agent = Agent(
        name="classifier",
        model="gemini-2.5-flash",
        instruction="Classify document type: invoice, contract, report, or other. Return ONLY the type.",
    )
    entity_agent = Agent(
        name="entity-extractor",
        model="gemini-2.5-flash",
        instruction="Extract: vendor, customer, total_amount, due_date, payment_terms. Return as JSON.",
    )

    async def parallel_stage():
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor(max_workers=2) as pool:
            return await asyncio.gather(
                loop.run_in_executor(pool, run_agent_sync, classify_agent, SAMPLE_INVOICE),
                loop.run_in_executor(pool, run_agent_sync, entity_agent, SAMPLE_INVOICE),
            )

    classify_result, entity_result = asyncio.run(parallel_stage())
    print(f"\n[CLASSIFY] {classify_result.strip()}")
    print(f"\n[ENTITIES]\n{entity_result}")

    # Stage 3: Validate
    validate_agent = Agent(
        name="validator",
        model="gemini-2.5-flash",
        instruction="Cross-check: do the extracted line items sum to the total? Flag discrepancies.",
    )
    validation = run_agent_sync(
        validate_agent,
        f"Validate:\n{entity_result}\n\nAgainst source:\n{SAMPLE_INVOICE}",
    )
    print(f"\n[VALIDATE]\n{validation}")


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
