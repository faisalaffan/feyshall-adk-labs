---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Parallel Agents (Fan-Out / Fan-In)

## Concept

Send the same input to multiple agents, run them concurrently, then combine results. This maximizes throughput when agents work on independent aspects of the same problem.

```
              ┌─► Agent A (sentiment) ─┐
User Input ───┼─► Agent B (entities)  ──┼──► Combiner ──► Output
              └─► Agent C (topics)    ──┘
```

## Code

```python
import asyncio
from google.adk.agents import Agent

sentiment_agent = Agent(
    name="sentiment",
    model="gemini-2.5-flash",
    instruction="Analyze sentiment of the text. Return: {'sentiment': 'positive'|'negative'|'neutral', 'score': -1.0 to 1.0}.",
)

entities_agent = Agent(
    name="entities",
    model="gemini-2.5-flash",
    instruction="Extract named entities (people, companies, locations). Return JSON array.",
)

topics_agent = Agent(
    name="topics",
    model="gemini-2.5-flash",
    instruction="Identify 1-3 main topics. Return JSON array of strings.",
)

combiner_agent = Agent(
    name="combiner",
    model="gemini-2.5-flash",
    instruction="Merge sentiment, entities, and topics into a unified analysis report.",
)

async def parallel_analyze(text: str) -> str:
    """Run all three analysis agents concurrently."""
    results = await asyncio.gather(
        run_agent_async(sentiment_agent, text),
        run_agent_async(entities_agent, text),
        run_agent_async(topics_agent, text),
    )

    combined_input = f"""
    Sentiment: {results[0]}
    Entities: {results[1]}
    Topics: {results[2]}
    """

    return run_agent(combiner_agent, combined_input)

async def run_agent_async(agent, input_text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, run_agent_sync, agent, input_text)
```

## Fan-Out/Fan-In Pattern Checklist

- [ ] Each parallel agent works on an **independent** aspect
- [ ] No agent depends on another agent's output
- [ ] Combiner agent handles **missing or partial** results gracefully
- [ ] Set a timeout — don't let one slow agent block the fan-in

## Pitfalls

- **Stragler effect**: If one agent takes 10s and others take 1s, total time = 10s. Set `asyncio.timeout()` per agent.
- **Combiner is a single point**: If the combiner hallucinates the merge, all parallel work is wasted. Add validation.
- **Cost multiplication**: 3 parallel agents = 3× LLM calls per user request. Budget accordingly.
