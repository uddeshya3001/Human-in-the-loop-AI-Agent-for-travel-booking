"""
Activities and tours search tool - returns mock activity options.
"""

from config.settings import MAX_ACTIVITY_OPTIONS


def tool_search_activities(city, days, interests, budget_usd):
    """
    Search for activities and tours in a city.
    
    Args:
        city: City name
        days: Number of days
        interests: List of interests or comma-separated string
        budget_usd: Activity budget in USD
    
    Returns:
        Dictionary with tool name and activity results
    """
    per_activity_budget = max(30, int(budget_usd / max(days, 1)))
    
    # Convert interests to list if string
    if isinstance(interests, str):
        interests = [i.strip() for i in interests.split(",")]
    
    all_activities = [
        {
            "name": f"{city} Museum Pass",
            "category": "Culture",
            "price_usd": int(per_activity_budget * 0.6),
            "duration_hours": 3.0,
            "description": "Access to top museums",
            "rating": 4.6
        },
        {
            "name": f"{city} Food Tour",
            "category": "Food & Drink",
            "price_usd": int(per_activity_budget * 0.9),
            "duration_hours": 3.5,
            "description": "Sample local cuisine",
            "rating": 4.8
        },
        {
            "name": f"{city} City Walking Tour",
            "category": "Sightseeing",
            "price_usd": int(per_activity_budget * 0.5),
            "duration_hours": 2.5,
            "description": "Guided historical tour",
            "rating": 4.5
        },
        {
            "name": f"Day Trip from {city}",
            "category": "Adventure",
            "price_usd": int(per_activity_budget * 1.3),
            "duration_hours": 8.0,
            "description": "Explore nearby attractions",
            "rating": 4.7
        },
        {
            "name": f"{city} River Cruise",
            "category": "Leisure",
            "price_usd": int(per_activity_budget * 0.8),
            "duration_hours": 2.0,
            "description": "Scenic river tour",
            "rating": 4.4
        },
        {
            "name": f"{city} Cooking Class",
            "category": "Food & Drink",
            "price_usd": int(per_activity_budget * 1.1),
            "duration_hours": 4.0,
            "description": "Learn local recipes",
            "rating": 4.9
        },
    ]
    
    # Sort by rating and return top options
    sorted_activities = sorted(all_activities, key=lambda x: x["rating"], reverse=True)[:MAX_ACTIVITY_OPTIONS]
    
    return {
        "tool": "search_activities",
        "results": sorted_activities
    }