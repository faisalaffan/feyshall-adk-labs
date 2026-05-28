# Java Setup

## Prerequisites

- JDK 17+
- Maven or Gradle

## Install ADK

```xml
<!-- pom.xml -->
<dependency>
    <groupId>com.google.adk</groupId>
    <artifactId>adk-java</artifactId>
    <version>1.2.0</version>
</dependency>
```

## Verify

```bash
mvn verify
```

## Create Your First Agent

```java
import com.google.adk.agents.FunctionTool;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import java.util.List;

public class HelloWorld {

    public static String greet(FunctionTool.Args args) {
        String name = args.getString("name");
        return "Hello, " + name + "!";
    }

    public static void main(String[] args) throws Exception {
        LlmAgent agent = LlmAgent.builder()
            .name("hello-world")
            .model("gemini-flash-latest")
            .instruction("You are a friendly assistant.")
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

        runner.run("Hi, my name is Faisal", sessionId)
            .forEach(event -> {
                if (event.content() != null) {
                    System.out.print(event.content());
                }
            });
    }
}
```

## Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key"
```
