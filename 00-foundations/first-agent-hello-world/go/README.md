---
adk_version: "1.2.0"
level: beginner
languages: [go]
---

# First Agent — Hello World (Go)

## Concept

ADK Go SDK follows the same agent loop as Python but uses Go idioms: explicit error handling, context propagation, and `AgentConfig` builders.

## Prerequisites

```bash
go mod init hello-adk
go get google.golang.org/adk@v1.2.0
export GOOGLE_API_KEY="your-api-key"
```

## Code

```go
package main

import (
    "context"
    "fmt"
    "os"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
    "google.golang.org/adk/tool/functiontool"
)

func greet(name string) string {
    return fmt.Sprintf("Hello, %s! Welcome to ADK.", name)
}

func main() {
    ctx := context.Background()

    agent, err := llmagent.New(
        llmagent.WithName("hello-world"),
        llmagent.WithModel("gemini-2.5-flash"),
        llmagent.WithInstruction("You are a friendly assistant. Use the greet tool when someone tells you their name."),
        llmagent.WithTools(functiontool.New(greet)),
    )
    if err != nil {
        fmt.Fprintf(os.Stderr, "error creating agent: %v\n", err)
        os.Exit(1)
    }

    r := runner.New(agent)
    sess := session.NewInMemory()

    events, err := r.Run(ctx, "My name is Faisal", sess)
    if err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }

    for ev := range events {
        if ev.Content != "" {
            fmt.Print(ev.Content)
        }
    }
    fmt.Println()
}
```

## Pitfalls

- **Context propagation**: Always pass `context.Background()` (or a derived context) — it carries deadlines and cancellation.
- **Channel-based streaming**: `runner.Run()` returns an event channel. The agent runs concurrently; the channel closes when the agent finishes.
- **Error handling is explicit**: Unlike Python's generator, Go separates errors from the event stream. Always check `err` before iterating.
