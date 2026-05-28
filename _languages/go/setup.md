# Go Setup

## Prerequisites

- Go 1.25+

## Install ADK

```bash
go get google.golang.org/adk@latest
```

## Verify

```bash
go run . --version
```

## Create Your First Agent

```go
package main

import (
    "context"
    "fmt"

    "google.golang.org/adk/agent/llmagent"
    "google.golang.org/adk/tool/functiontool"
    "google.golang.org/adk/runner"
    "google.golang.org/adk/session"
)

func greet(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}

func main() {
    ctx := context.Background()

    agent, _ := llmagent.New(
        llmagent.WithName("hello-world"),
        llmagent.WithModel("gemini-2.5-flash"),
        llmagent.WithTools(functiontool.New(greet)),
    )

    r := runner.New(agent)
    sess := session.NewInMemory()
    // Run agent with r.Run(ctx, input, sess)...
}
```

## Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key"
```
