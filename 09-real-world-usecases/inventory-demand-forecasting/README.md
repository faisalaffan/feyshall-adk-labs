---
adk_version: "1.28"
level: advanced
languages: [python]
---

# Inventory Demand Forecasting

## Concept

Real-world agent for retail/ERP inventory forecasting. Combines historical sales data, seasonal trends, and external factors (holidays, weather) to predict demand.

## Architecture

```
User: "Forecast demand for SKU-123 next month"
   │
   ▼
Orchestrator Agent
   ├──► fetch_historical_sales(sku)    → DB query
   ├──► check_seasonal_trends(sku)     → Analytics API
   ├──► fetch_external_factors()       → Weather API, holiday calendar
   └──► generate_forecast(data)        → ML model or statistical
   │
   ▼
Response: "Predicted demand: 1,200 units (±15%). Key factors: Ramadan +30%, rainy season -5%."
```

## Code Skeleton

```python
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
import pandas as pd

def fetch_historical_sales(sku: str, months: int = 12) -> dict:
    """Fetch historical sales data for a product SKU."""
    query = """
        SELECT month, SUM(quantity) as units, AVG(unit_price) as price
        FROM sales WHERE sku = ? AND date >= DATE_SUB(NOW(), INTERVAL ? MONTH)
        GROUP BY month ORDER BY month
    """
    rows = db.execute(query, (sku, months))
    return {"sku": sku, "history": rows}

def check_seasonal_trends(sku: str) -> dict:
    """Check seasonal patterns for a product category."""
    category = get_category(sku)
    trends = analytics.get_seasonal_multipliers(category)
    return {"category": category, "multipliers": trends}

def fetch_external_factors(month: str) -> dict:
    """Fetch external factors affecting demand."""
    return {
        "holidays": calendar.get_holidays(month),
        "weather_forecast": weather.get_monthly_forecast(month),
        "economic_indicators": econ.get_consumer_confidence(),
    }

agent = Agent(
    name="inventory-forecaster",
    model="gemini-2.5-pro",  # Stronger reasoning for numerical analysis
    instruction="""You are an inventory demand forecaster. For each request:
    1. Fetch historical sales data
    2. Apply seasonal multipliers
    3. Factor in external events (holidays, weather)
    4. Generate a forecast with confidence intervals
    5. Recommend order quantities""",
    tools=[
        FunctionTool(fetch_historical_sales),
        FunctionTool(check_seasonal_trends),
        FunctionTool(fetch_external_factors),
    ],
)
```

## Pitfalls

- **Over-reliance on LLM math**: LLMs do statistical approximation, not precise forecasting. Use the LLM for reasoning and tool orchestration; use Python/ML for actual forecasting.
- **Cold start**: New SKUs have no historical data. Fall back to category-level trends.
- **Bullwhip effect**: If the agent's forecast feeds directly into purchase orders, errors amplify up the supply chain. Always include human review for orders above a threshold.
