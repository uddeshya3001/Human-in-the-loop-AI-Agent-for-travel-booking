"""
Hotel search tool - returns mock hotel options.
"""

from config.settings import MAX_HOTEL_OPTIONS


def tool_search_hotels(city, nights, budget_usd):
    """
    Search for hotels in a city.
    
    Args:
        city: City name
        nights: Number of nights
        budget_usd: Hotel budget in USD
    
    Returns:
        Dictionary with tool name and hotel results
    """
    base = max(60, int(budget_usd / max(nights, 1)))
    
    picks = [
        {
            "name": "Central Boutique Hotel",
            "nightly_usd": int(base * 0.9),
            "total_usd": int(base * 0.9 * nights),
            "rating": 4.5,
            "location": "City Center",
            "amenities": ["WiFi", "Breakfast", "Gym"]
        },
        {
            "name": "Riverside Stay",
            "nightly_usd": int(base * 0.8),
            "total_usd": int(base * 0.8 * nights),
            "rating": 4.2,
            "location": "Riverside District",
            "amenities": ["WiFi", "Pool", "Restaurant"]
        },
        {
            "name": "Modern Loft Hotel",
            "nightly_usd": int(base * 1.1),
            "total_usd": int(base * 1.1 * nights),
            "rating": 4.7,
            "location": "Downtown",
            "amenities": ["WiFi", "Spa", "Rooftop Bar", "Gym"]
        },
    ]
    
    # Sort by price and return top options
    sorted_picks = sorted(picks, key=lambda x: x["nightly_usd"])[:MAX_HOTEL_OPTIONS]
    
    return {
        "tool": "search_hotels",
        "results": sorted_picks
    }