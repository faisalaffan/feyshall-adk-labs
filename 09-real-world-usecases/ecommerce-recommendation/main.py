"""E-Commerce Recommendation — SE Asian context.
Run: python 09-real-world-usecases/ecommerce-recommendation/main.py
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService


def get_user_profile(user_id: str) -> dict:
    """Fetch user purchase history and preferences."""
    return {
        "recent_views": ["Nike Air Max", "Adidas Ultraboost", "iPhone 16 case"],
        "price_range": "Rp 100,000 - Rp 2,500,000",
        "preferred_categories": ["fashion", "electronics"],
        "location": "Jakarta",
    }


def get_active_promos(user_id: str) -> list:
    """Get active promotions for the user."""
    return [
        {"type": "flash_sale", "discount": "30%", "ends": "2 hours"},
        {"type": "free_shipping", "min_order": "Rp 50,000"},
        {"type": "cashback", "amount": "10%", "max": "Rp 50,000"},
        {"type": "payday_deal", "discount": "15%", "note": "Valid 25th-1st"},
    ]


def get_product_context(product_id: str) -> dict:
    """Get product details and alternatives."""
    return {
        "product": "Nike Air Max 270",
        "price": 1899000,
        "category": "fashion/shoes",
        "rating": 4.7,
        "sold": 15420,
        "seller": "Nike Official Store",
        "alternatives": [
            {"name": "Adidas Ultraboost 23", "price": 2100000, "rating": 4.8},
            {"name": "Puma RS-X", "price": 1299000, "rating": 4.5},
        ],
    }


def main():
    print("E-Commerce Recommendation Demo (SE Asia Context)\n")

    agent = Agent(
        name="recommender",
        model="gemini-2.5-flash",
        description="E-commerce product recommender for Indonesian market",
        instruction="""You are a product recommendation engine for Indonesian e-commerce.
        Recommend products considering:
        1. User's browsing and purchase history
        2. Active promotions (flash sales, free shipping, cashback, payday deals)
        3. Product alternatives and social proof
        4. Local context: Harbolnas, Ramadan, payday cycles (25th-1st)
        5. COD preference in Indonesia
        Include a 'why' in Bahasa Indonesia for each recommendation.
        Limit to 3-5 recommendations.""",
        tools=[
            FunctionTool(get_user_profile),
            FunctionTool(get_active_promos),
            FunctionTool(get_product_context),
        ],
    )

    runner = Runner(agent=agent, session_service=InMemorySessionService())
    session = runner.session_service.create_session("recommend", "user-123")

    query = "What should I buy? I'm looking at Nike Air Max 270 (product ID SHOE-001)"
    print(f"Shopper: {query}\n")
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
