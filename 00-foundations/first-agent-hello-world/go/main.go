package main

import (
    "context"
    "fmt"
    "os"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
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
