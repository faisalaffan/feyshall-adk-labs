---
adk_version: "1.28"
level: advanced
languages: [python]
---

# LangChain Tool Adapter

## Concept

If you have existing LangChain tools or want to use LangChain's 100+ integrations, wrap them as ADK tools via a thin adapter. This saves rewriting battle-tested integrations.

## Adapter Pattern

```python
from google.adk.tools import FunctionTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def adapt_langchain_tool(lc_tool):
    """Wrap a LangChain tool as an ADK-compatible function."""

    def wrapper(**kwargs):
        # LangChain tools use a single JSON string input by default
        result = lc_tool.run(kwargs)
        return result

    # Copy metadata for LLM discovery
    wrapper.__name__ = lc_tool.name
    wrapper.__doc__ = lc_tool.description
    return wrapper

# Usage
wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
adapted_wiki = adapt_langchain_tool(wiki_tool)

agent = Agent(
    name="research-agent",
    model="gemini-2.5-flash",
    tools=[FunctionTool(adapted_wiki)],
)
```

## Structured Tool Adapter (Better)

```python
from typing import Annotated
from pydantic import BaseModel, Field

class LangChainToolAdapter:
    """Properly wrap LangChain tools with typed parameters."""

    def __init__(self, lc_tool, input_schema: type[BaseModel]):
        self.lc_tool = lc_tool
        self.input_schema = input_schema

    def __call__(self, **kwargs):
        validated = self.input_schema(**kwargs)
        result = self.lc_tool.run(validated.model_dump())
        return result

# Example: Wrap Tavily Search
from langchain_community.tools.tavily_search import TavilySearchResults

class SearchInput(BaseModel):
    query: str = Field(description="Search query string")

tavily = TavilySearchResults(max_results=5)
adapted_search = LangChainToolAdapter(tavily, SearchInput)

agent = Agent(
    name="search-agent",
    model="gemini-2.5-flash",
    tools=[FunctionTool(adapted_search)],
)
```

## When to Use This vs MCP

| | LangChain Adapter | MCP Tool |
|---|---|---|
| **Setup** | Write adapter code | Point to MCP server |
| **Tool coverage** | 100+ LangChain integrations | 100+ MCP servers |
| **Latency** | Direct function call | Subprocess + handshake |
| **Auth** | LangChain's built-in auth | MCP server handles auth |
| **Best for** | Existing LangChain codebase | Greenfield, standardized protocol |

## Pitfalls

- **LangChain deprecation churn**: LangChain APIs change frequently. Pin your `langchain` version and test adapters on upgrades.
- **Input format mismatch**: LangChain tools often expect a single string or a specific dict format. Always use the structured adapter (pydantic) for reliability.
- **Async support**: LangChain tools are typically sync. If your ADK agent uses `async_tools/`, the LangChain adapter blocks the event loop. Wrap with `asyncio.to_thread()`.
