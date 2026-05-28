---
adk_version: "1.28"
level: beginner
languages: [java]
---

# First Agent — Hello World (Java)

## Concept

ADK Java SDK uses builders and reactive streams. The agent loop returns `Flow<Event>` for streaming support.

## Prerequisites

```xml
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>adk-java</artifactId>
    <version>1.28.0</version>
</dependency>
```

```bash
export GOOGLE_API_KEY="your-api-key"
```

## Code

```java
package com.feyshall.cookbook;

import com.google.adk.agent.Agent;
import com.google.adk.runner.Runner;
import com.google.adk.session.InMemorySessionService;
import com.google.adk.session.Session;
import com.google.adk.tool.FunctionTool;
import java.util.List;
import java.util.concurrent.Flow;

public class HelloWorld {

    public static String greet(String name) {
        return "Hello, " + name + "! Welcome to ADK.";
    }

    public static void main(String[] args) throws Exception {
        Agent agent = Agent.builder()
            .name("hello-world")
            .model("gemini-2.5-flash")
            .instruction("You are a friendly assistant. Use the greet tool when someone tells you their name.")
            .tools(List.of(FunctionTool.from(HelloWorld.class, "greet")))
            .build();

        Runner runner = Runner.builder()
            .agent(agent)
            .sessionService(new InMemorySessionService())
            .build();

        Session session = runner.sessionService()
            .createSession("hello-world", "user-1");

        Flow.Publisher<Runner.Event> events = runner.run(
            "My name is Faisal", session
        );

        events.subscribe(new Flow.Subscriber<>() {
            public void onNext(Runner.Event event) {
                if (event.content() != null) {
                    System.out.print(event.content());
                }
            }
            public void onComplete() { System.out.println(); }
            public void onError(Throwable t) { t.printStackTrace(); }
            public void onSubscribe(Flow.Subscription s) { s.request(Long.MAX_VALUE); }
        });

        Thread.sleep(5000); // Wait for async completion
    }
}
```

## Pitfalls

- **Reactive streams**: ADK Java uses `Flow.Publisher` — you must subscribe to receive events. Don't forget to `request(n)`.
- **Thread blocking**: The main thread exits before the agent finishes. Use `Thread.sleep()` or a `CountDownLatch` in examples; use proper async handling in production.
- **Method reference tool binding**: `FunctionTool.from(Class, methodName)` uses reflection. Ensure your tool methods are `public static`.
