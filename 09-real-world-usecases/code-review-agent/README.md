---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Code Review Agent

## Concept

Multi-agent code review: one agent checks style, one checks security, one checks logic. Each specializes in its domain, and a coordinator merges findings into a single review.

## Architecture

```
PR Diff
    │
    ├──► Style Agent (linting, formatting, naming)
    ├──► Security Agent (injection, secrets, unsafe patterns)  
    └──► Logic Agent (bugs, edge cases, performance)
    │
    ▼
Merge Agent → Single PR review comment
```

## Code Skeleton

```python
style_agent = Agent(
    name="style-reviewer",
    model="gemini-2.5-flash",
    instruction="""Review code for style issues:
    - Naming conventions (snake_case, descriptive names)
    - Function length (<50 lines)
    - Missing type hints
    - Formatting consistency
    Return only actionable issues, not praise.""",
)

security_agent = Agent(
    name="security-reviewer",
    model="gemini-2.5-flash",
    instruction="""Review code for security issues:
    - Hardcoded credentials or API keys
    - SQL/command injection vectors
    - Unsafe deserialization (pickle, eval, exec)
    - Missing input validation
    - Insecure cryptography (MD5, SHA1, weak keys)
    Flag anything that could be exploited in production.""",
)

logic_agent = Agent(
    name="logic-reviewer",
    model="gemini-2.5-pro",  # Needs stronger reasoning
    instruction="""Review code for logic issues:
    - Off-by-one errors
    - None/empty handling
    - Race conditions
    - Resource leaks (unclosed files, connections)
    - Inefficient algorithms (O(n²) where O(n) would work)""",
)

merge_agent = Agent(
    name="review-merge",
    model="gemini-2.5-flash",
    instruction="""Merge findings from style, security, and logic reviewers into
    a single, well-organized code review. Group by file and severity.
    Format as GitHub-flavored markdown with code suggestions.""",
)

# Orchestration
async def review_pr(diff: str) -> str:
    results = await asyncio.gather(
        run_agent_async(style_agent, diff),
        run_agent_async(security_agent, diff),
        run_agent_async(logic_agent, diff),
    )
    combined = f"""
    ## Style
    {results[0]}

    ## Security
    {results[1]}

    ## Logic
    {results[2]}
    """
    return run_agent(merge_agent, combined)
```

## Pitfalls

- **False positives erode trust**: If the security agent flags `os.environ["KEY"]` as "hardcoded," developers ignore it. Tune prompts to reduce noise.
- **Review latency**: 4 sequential agent calls → 5-15 seconds. For large PRs, consider running only on changed files.
- **Missing context**: The agent sees the diff, not the codebase. It can't know if a pattern is consistent with the rest of the project.
