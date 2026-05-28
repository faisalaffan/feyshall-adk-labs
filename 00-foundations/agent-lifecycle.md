---
adk_version: "1.28"
level: beginner
languages: [python]
---

# Agent Lifecycle

## Concept

Every ADK agent follows a deterministic state machine. Understanding this loop is critical for debugging unexpected behavior, tool call failures, and infinite loops.

```
         ┌──────────┐
         │   init    │
         └────┬─────┘
              ▼
      ┌───────────────┐
      │  llm_generate  │◄─────────────────┐
      └───────┬───────┘                   │
              │                           │
         has_tool_calls?                  │
          │         │                     │
         yes        no                    │
          ▼          ▼                    │
   ┌──────────┐  ┌──────────┐            │
   │tool_exec │  │ respond  │────────────►│
   └────┬─────┘  └──────────┘  (final)   │
        │                                 │
        ▼                                 │
   return results ────────────────────────┘
   (loop back to llm_generate)
```

## States

| State | What Happens |
|-------|-------------|
| `init` | Agent loads config, tools, system prompt. Session is created or restored. |
| `llm_generate` | Model receives conversation history + tool definitions, produces either text or tool calls. |
| `tool_exec` | Runner executes tool calls in parallel or sequence. Results are formatted and appended to history. |
| `respond` | Final text response is streamed to the user. Session state is persisted. |

## Key Behaviors

- **Max turns**: ADK caps the LLM→Tool→LLM loop at a configurable limit (default: 10). After that, it forces a response.
- **Parallel tools**: If the model returns multiple tool calls in one response, ADK executes them concurrently by default.
- **Tool errors don't crash**: By default, exceptions in tools are caught, formatted as error messages, and fed back to the LLM for recovery.

## Pitfalls

- **Infinite loops**: If a tool always returns results the LLM can't act on, the agent loops until `max_turns`. Always set a reasonable turn limit.
- **Silent tool failures**: Tool exceptions are returned as text to the LLM, not raised. If the LLM ignores the error, the user never sees it. Log tool errors explicitly.
- **Session bloat**: Every turn appends to the conversation history. Long sessions exceed context windows. Use `context-compaction.md` strategies.
