package com.feyshall.cookbook;

import com.google.adk.agents.FunctionTool;
import com.google.adk.agents.LlmAgent;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import java.util.List;

public class HelloWorld {

    public static String greet(String name) {
        return "Hello, " + name + "! Welcome to ADK.";
    }

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
