"""Inventory Demand Forecasting — runnable example.
Run: python 09-real-world-usecases/inventory-demand-forecasting/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def fetch_historical_sales(sku: str, months: int = 12) -> dict:
    """Fetch historical sales data for a product SKU."""
    sales_data = {
        "SKU-123": [
            {"month": "2026-01", "units": 120, "price": 50000},
            {"month": "2026-02", "units": 135, "price": 50000},
            {"month": "2026-03", "units": 200, "price": 50000},  # Ramadan spike
            {"month": "2026-04", "units": 110, "price": 50000},
            {"month": "2026-05", "units": 130, "price": 50000},
        ],
    }
    return {"sku": sku, "history": sales_data.get(sku, [])}


def check_seasonal_trends(sku: str) -> dict:
    """Check seasonal patterns for a product category."""
    return {
        "category": "food_beverage",
        "ramadan_multiplier": 1.5,
        "weekend_multiplier": 1.2,
        "payday_multiplier": 1.3,
    }


def fetch_external_factors(month: str) -> dict:
    """Fetch external factors affecting demand."""
    return {
        "holidays": ["Idul Fitri (estimated)", "Labor Day"],
        "weather": "Rainy season — foot traffic decreases 15%",
        "economic": "Consumer confidence index: 125 (positive)",
    }


def main():
    agent = Agent(
        name="inventory-forecaster",
        model="gemini-2.5-flash",
        description="Demand forecasting agent for retail",
        instruction="""You are a demand forecaster. For each SKU:
        1. Fetch historical sales
        2. Check seasonal trends
        3. Fetch external factors
        4. Generate forecast with confidence intervals
        5. Recommend order quantity""",
        tools=[
            FunctionTool(fetch_historical_sales),
            FunctionTool(check_seasonal_trends),
            FunctionTool(fetch_external_factors),
        ],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("forecast", "analyst-1")

    query = "Forecast demand for SKU-123 for next month (June 2026)"
    print(f"Analyst: {query}\n")
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
