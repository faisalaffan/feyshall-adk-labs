"""LangChain Tool Adapter — runnable example.
Wraps LangChain-style tools for use in ADK agents.
Run: python 01-tools/langchain-tool-adapter/main.py
"""
import os
from typing import Annotated
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


# --- Simulated LangChain-style tool ---
class SimulatedLangChainTool:
    """Simulates a LangChain community tool (e.g., Wikipedia, Tavily)."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, input_data) -> str:
        # In production: this calls the actual LangChain tool
        return f"[{self.name}] Result for: {input_data}"


# --- ADK Adapter ---
class SearchInput(BaseModel):
    query: str = Field(description="Search query string")


class LangChainToolAdapter:
    """Wrap a LangChain-style tool for ADK with typed input schema."""

    def __init__(self, lc_tool, input_schema: type[BaseModel]):
        self.lc_tool = lc_tool
        self.input_schema = input_schema

    def __call__(self, **kwargs):
        validated = self.input_schema(**kwargs)
        result = self.lc_tool.run(validated.model_dump())
        return result


def main():
    print("LangChain Tool Adapter Demo\n")

    # Create a simulated LangChain search tool
    wiki_tool = SimulatedLangChainTool(
        name="wikipedia",
        description="Search Wikipedia articles",
    )

    # Wrap it for ADK
    adapted_wiki = LangChainToolAdapter(wiki_tool, SearchInput)

    agent = Agent(
        name="research-agent",
        model="gemini-2.5-flash",
        description="Agent using LangChain-adapted tools",
        instruction="Use the wikipedia_search tool to find information before answering.",
        tools=[
            FunctionTool(adapted_wiki, name="wikipedia_search"),
        ],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("research", "user-1")

    query = "Search Wikipedia for information about Jakarta"
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
