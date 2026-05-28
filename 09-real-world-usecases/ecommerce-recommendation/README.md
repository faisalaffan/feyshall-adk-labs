---
adk_version: "1.28"
level: advanced
languages: [python]
---

# E-Commerce Recommendation

## Concept

Product recommendation agent for SE Asian e-commerce platforms (Tokopedia, Shopee-style). Combines user behavior, purchase history, and local context (promo days, regional preferences).

## Architecture

```
User browses product page
    │
    ▼
Context Agent (current product, user history, session data)
    │
    ├──► Recommendations Agent (similar products, frequently bought together)
    ├──► Promo Agent (active promos, flash sales, free shipping thresholds)
    └──► Social Proof Agent (reviews, ratings, popularity signals)
    │
    ▼
Ranking Agent (merge + rank by predicted conversion)
    │
    ▼
Response: personalized widget with explanation
```

## Code Skeleton

```python
def get_user_profile(user_id: str) -> dict:
    """Fetch user's purchase history, browsing, wishlist."""
    return {
        "recent_views": db.get_recent_views(user_id, limit=20),
        "purchase_history": db.get_purchases(user_id, limit=50),
        "price_range": analytics.get_price_preference(user_id),
        "preferred_categories": analytics.get_category_affinity(user_id),
    }

def get_product_context(product_id: str) -> dict:
    """Get current product details and related data."""
    product = db.get_product(product_id)
    return {
        "product": product,
        "category": product["category"],
        "price": product["price"],
        "seller": db.get_seller(product["seller_id"]),
    }

def get_active_promos(user_id: str, category: str) -> list:
    """Get active promotions relevant to user and category."""
    return promo_engine.get_active_promos(
        user_id=user_id,
        category=category,
        include=["flash_sale", "free_shipping", "cashback", "voucher"],
    )

def get_social_proof(product_ids: list[str]) -> dict:
    """Get review summaries and popularity signals."""
    return {
        pid: {
            "rating": reviews.get_avg_rating(pid),
            "review_count": reviews.get_count(pid),
            "sold_count": analytics.get_sold_count(pid, window_days=30),
            "return_rate": analytics.get_return_rate(pid),
        }
        for pid in product_ids
    }

recommendation_agent = Agent(
    name="recommender",
    model="gemini-2.5-flash",
    instruction="""You are a product recommendation engine for an Indonesian e-commerce platform.
    Generate personalized recommendations considering:
    1. User's browsing and purchase history
    2. Current product context (category, price range)
    3. Active promotions and flash sales
    4. Social proof (ratings, reviews, popularity)
    5. Local factors: Harbolnas, Ramadan, payday cycles (25th-1st)

    For each recommendation, include a short "why" in Bahasa Indonesia.
    Limit to 5 recommendations.""",
    tools=[
        FunctionTool(get_user_profile),
        FunctionTool(get_product_context),
        FunctionTool(get_active_promos),
        FunctionTool(get_social_proof),
    ],
)
```

## SE Asian Context

| Factor | Impact on Recommendations |
|--------|--------------------------|
| Harbolnas (11.11, 12.12) | Heavily discount electronics, fashion |
| Ramadan | Food, fashion, gifts spike |
| Payday (25th-1st) | Higher conversion, suggest higher-ticket items |
| COD preference | Don't suggest items with high return rates |
| Mobile-first | Optimize for small screens (short descriptions) |

## Pitfalls

- **Cold start for new users**: No purchase history = generic recommendations. Use trending/regional popularity as fallback.
- **Promo-driven distortion**: Users buy what's discounted, not what they need. Recommendation quality metrics must account for promo influence.
- **Seller gaming**: Sellers use fake purchases to boost "sold count." Cross-reference with return rates to detect manipulation.
