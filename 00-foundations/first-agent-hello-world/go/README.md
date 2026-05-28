---
adk_version: "1.28"
level: beginner
languages: [go]
---

# First Agent — Hello World (Go)

## Concept

ADK Go SDK follows the same agent loop as Python but uses Go idioms: explicit error handling, context propagation, and `AgentConfig` builders.

## Prerequisites

```bash
go mod init hello-adk
go get github.com/google/adk-go@v1.28
export GOOGLE_API_KEY="your-api-key"
```

## Code

```go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/google/adk-go/agent"
    "github.com/google/adk-go/runner"
    "github.com/google/adk-go/session"
    "github.com/google/adk-go/tool"
)

func greet(name string) string {
    return fmt.Sprintf("Hello, %s! Welcome to ADK.", name)
}

func main() {
    ctx := context.Background()

    a := agent.New(
        agent.WithName("hello-world"),
        agent.WithModel("gemini-2.5-flash"),
        agent.WithInstruction("You are a friendly assistant. Use the greet tool when someone tells you their name."),
        agent.WithTools(tool.NewFunction(greet)),
    )

    r := runner.New(a)
    sess := session.NewInMemory("user-1")

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
- **Channel-based streaming**: `r.Run()` returns a channel. The agent runs concurrently; the channel closes when the agent finishes.
- **Error handling is explicit**: Unlike Python's generator, Go separates errors from the event stream. Always check `err` before iterating.
