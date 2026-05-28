"""Tool With Auth — runnable example.
Run: python 01-tools/tool-with-auth/main.py

Demonstrates secure API key handling: never hardcode, always from env.
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def send_notification(channel: str, message: str) -> str:
    """Send a notification to a channel. Uses API key from env, never hardcoded.

    Args:
        channel: Target channel (e.g., 'slack', 'email').
        message: Message body.
    """
    token = os.environ.get("NOTIFICATION_API_KEY", "demo-token")
    # In production: call actual API with token
    return f"[{channel.upper()}] Message sent with token ...{token[-4:]}: {message}"


def query_database(query: str) -> list:
    """Execute a database query. Credentials from env, never in code.

    Args:
        query: SQL query to execute.
    """
    db_url = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/demo")
    # In production: connect with db_url, execute query
    return [{"status": "ok", "query": query[:50], "source": db_url.split("@")[-1]}]


def main():
    agent = Agent(
        name="auth-demo",
        model="gemini-2.5-flash",
        description="Demonstrates secure tool configuration",
        instruction="Use available tools. Show the token/URL masks for security.",
        tools=[FunctionTool(send_notification), FunctionTool(query_database)],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("auth-demo", "user-1")

    query = "Send a message to the dev channel: deployment successful, then check the deployments table"
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
