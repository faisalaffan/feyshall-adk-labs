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
