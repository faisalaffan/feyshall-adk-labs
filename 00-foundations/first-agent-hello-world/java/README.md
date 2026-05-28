---
adk_version: "1.2.0"
level: beginner
languages: [java]
---

# First Agent — Hello World (Java)

## Concept

ADK Java SDK uses builders with `LlmAgent` as the primary agent class. The runner returns an iterable stream for processing events.

## Prerequisites

```xml
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>adk-java</artifactId>
    <version>1.2.0</version>
</dependency>
```

```bash
export GOOGLE_API_KEY="your-api-key"
```

## Code

```java
package com.feyshall.cookbook;

import com.google.adk.agents.FunctionTool;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import java.util.List;

public class HelloWorld {

    public static String greet(FunctionTool.Args args) {
        String name = args.getString("name");
        return "Hello, " + name + "! Welcome to ADK.";
    }

    public static void main(String[] args) throws Exception {
        LlmAgent agent = LlmAgent.builder()
            .name("hello-world")
            .model("gemini-flash-latest")
            .instruction("You are a friendly assistant. Use the greet tool when someone tells you their name.")
            .tools(List.of(
                FunctionTool.create("greet", HelloWorld.class, "greet")
                    .description("Greet someone by name")
                    .parameter("name", FunctionTool.ParamType.STRING, "Person's name")
                    .build()
            ))
            .build();

        Runner runner = Runner.builder()
            .agent(agent)
            .sessionService(new InMemorySessionService())
            .build();

        String sessionId = runner.sessionService()
            .createSession("hello-world", "user-1");

        runner.run("My name is Faisal", sessionId)
            .forEach(event -> {
                if (event.content() != null) {
                    System.out.print(event.content());
                }
            });
        System.out.println();
    }
}
```

## Pitfalls

- **LlmAgent is the primary class**: Use `LlmAgent.builder()`, not `Agent.builder()`.
- **FunctionTool uses builder pattern**: `FunctionTool.create(name, class, method).description(...).parameter(...).build()`.
- **Model names**: Use `gemini-flash-latest` for automatic updates, or pin to a specific version.
