package com.feyshall.cookbook;

import com.google.adk.agent.Agent;
import com.google.adk.runner.Runner;
import com.google.adk.session.InMemorySessionService;
import com.google.adk.session.Session;
import com.google.adk.tool.FunctionTool;
import java.util.List;
import java.util.concurrent.CountDownLatch;
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

        CountDownLatch latch = new CountDownLatch(1);
        Flow.Publisher<Runner.Event> events = runner.run(
            "My name is Faisal", session
        );

        events.subscribe(new Flow.Subscriber<>() {
            private Flow.Subscription sub;

            public void onSubscribe(Flow.Subscription s) {
                sub = s;
                s.request(1);
            }

            public void onNext(Runner.Event event) {
                if (event.content() != null) {
                    System.out.print(event.content());
                }
                sub.request(1);
            }

            public void onComplete() {
                System.out.println();
                latch.countDown();
            }

            public void onError(Throwable t) {
                t.printStackTrace();
                latch.countDown();
            }
        });

        latch.await();
    }
}
