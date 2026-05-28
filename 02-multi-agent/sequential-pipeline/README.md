---
adk_version: "1.28"
level: intermediate
languages: [python]
---

# Sequential Pipeline

## Concept

Chain agents where each agent's output becomes the next agent's input. This is the simplest multi-agent pattern — like Unix pipes for AI.

```
User Input → Agent A → Agent B → Agent C → Final Output
              (extract)  (analyze)  (format)
```

## Code

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Agent A: Extract structured data from free text
extractor = Agent(
    name="extractor",
    model="gemini-2.5-flash",
    instruction="Extract person name, company, and role from the input. Return JSON.",
)

# Agent B: Analyze the extracted data
analyzer = Agent(
    name="analyzer",
    model="gemini-2.5-flash",
    instruction="Given a JSON object with name/company/role, assess if they're a decision-maker. Return: {'decision_maker': true/false, 'confidence': 0-1}.",
)

# Agent C: Format the final output
formatter = Agent(
    name="formatter",
    model="gemini-2.5-flash",
    instruction="Format the analysis into a one-line summary for a CRM system.",
)

def pipeline(user_input: str) -> str:
    """Run agents in sequence, passing output to input."""
    extracted = run_agent(extractor, user_input)
    analyzed = run_agent(analyzer, extracted)
    formatted = run_agent(formatter, analyzed)
    return formatted

def run_agent(agent, input_text):
    """Helper: run a single agent and collect its text output."""
    session = runner.session_service.create_session(
        app_name=agent.name,
        user_id="pipeline",
    )
    output = []
    for event in runner_for(agent).run(input_text, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)
```

## When to Use

- Data transformation pipelines (extract → clean → enrich → store)
- Multi-step reasoning where each step has a different "personality"
- Approval workflows with distinct stages

## Pitfalls

- **Error propagation**: If Agent A returns bad JSON, Agent B fails silently. Add validation between stages.
- **Latency stack**: Sequential = sum of all agent latencies. 3 agents × 2s = 6s minimum. Use `parallel-agents/` when possible.
- **Context accumulation**: Each agent adds to the chain. The last agent sees the full history — can hit context limits.
