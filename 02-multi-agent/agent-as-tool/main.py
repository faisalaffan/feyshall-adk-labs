"""Agent as Tool — runnable example.
Wraps a specialist agent as a tool callable by the main agent.
Run: python 02-multi-agent/agent-as-tool/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

session_service = InMemorySessionService()


def run_agent(agent, user_input: str, user_id: str) -> str:
    runner = Runner(agent=agent, session_service=session_service)
    session = session_service.create_session(agent.name, user_id)
    output = []
    for event in runner.run(user_input=user_input, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    output.append(part.text)
    return "".join(output)


def main():
    # Specialist agent — wrapped as a tool
    translator = Agent(
        name="translator",
        model="gemini-2.5-flash",
        instruction="Translate to the requested language. Return ONLY the translation.",
    )

    def translate_tool(text: str, language: str) -> str:
        """Translate text to the specified language.

        Args:
            text: Text to translate.
            language: Target language (e.g., 'Indonesian', 'Japanese').
        """
        return run_agent(translator, f"Translate to {language}: {text}", "translator")

    # Main agent — uses translator as a tool
    main_agent = Agent(
        name="multilingual-assistant",
        model="gemini-2.5-flash",
        description="Agent that can translate via another agent",
        instruction="Help the user. Use translate_tool for translations when needed.",
        tools=[FunctionTool(translate_tool)],
    )

    runner = Runner(agent=main_agent, session_service=session_service)
    session = session_service.create_session("main", "user-1")

    query = "Translate 'Good morning, how are you?' to Indonesian"
    print(f"User: {query}")
    print("Agent: ", end="", flush=True)
    for event in runner.run(user_input=query, session=session):
        if event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Set GOOGLE_API_KEY environment variable to run.")
        exit(1)
    main()
