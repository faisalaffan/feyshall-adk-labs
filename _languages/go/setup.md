# Go Setup

## Prerequisites

- Go 1.21+

## Install ADK

```bash
go get github.com/google/adk-go
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
    "github.com/google/adk-go/agent"
    "github.com/google/adk-go/tool"
)

func greet(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}

func main() {
    a := agent.New(
        agent.WithName("hello-world"),
        agent.WithModel("gemini-2.5-flash"),
        agent.WithTools(tool.NewFunction(greet)),
    )
    // Run agent...
}
```

## Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key"
```
