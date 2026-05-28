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
    <version>0.1.0</version>
</dependency>
```

## Verify

```bash
mvn verify
```

## Create Your First Agent

```java
import com.google.adk.agent.Agent;
import com.google.adk.tool.FunctionTool;

public class HelloWorld {
    public static String greet(String name) {
        return "Hello, " + name + "!";
    }

    public static void main(String[] args) {
        Agent agent = Agent.builder()
            .name("hello-world")
            .model("gemini-2.5-flash")
            .tools(List.of(FunctionTool.from(HelloWorld.class, "greet")))
            .build();
        // Run agent...
    }
}
```

## Environment Variables

```bash
export GOOGLE_API_KEY="your-api-key"
```
