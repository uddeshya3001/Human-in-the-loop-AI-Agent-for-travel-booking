"""
Car rental search tool - returns mock car rental options.
"""

from config.settings import MAX_CAR_OPTIONS


def tool_search_cars(city, pickup_date, return_date, budget_usd, days):
    """
    Search for car rentals in a city.
    
    Args:
        city: City name
        pickup_date: Pickup date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        budget_usd: Car rental budget in USD
        days: Number of rental days
    
    Returns:
        Dictionary with tool name and car rental results
    """
    daily_base = max(30, int(budget_usd / max(days, 1)))
    
    options = [
        {
            "company": "EasyRent",
            "car_type": "Compact",
            "model": "Toyota Corolla or similar",
            "daily_usd": int(daily_base * 0.7),
            "total_usd": int(daily_base * 0.7 * days),
            "features": ["Automatic", "A/C", "4 doors"],
            "pickup_location": f"{city} Airport"
        },
        {
            "company": "DriveNow",
            "car_type": "SUV",
            "model": "Honda CR-V or similar",
            "daily_usd": int(daily_base * 1.2),
            "total_usd": int(daily_base * 1.2 * days),
            "features": ["Automatic", "A/C", "5 seats", "GPS"],
            "pickup_location": f"{city} Downtown"
        },
        {
            "company": "LuxDrive",
            "car_type": "Luxury",
            "model": "BMW 5 Series or similar",
            "daily_usd": int(daily_base * 1.8),
            "total_usd": int(daily_base * 1.8 * days),
            "features": ["Automatic", "Premium Sound", "Leather", "GPS"],
            "pickup_location": f"{city} City Center"
        },
    ]
    
    # Sort by price and return top options
    sorted_options = sorted(options, key=lambda x: x["daily_usd"])[:MAX_CAR_OPTIONS]
    
    return {
        "tool": "search_cars",
        "results": sorted_options
    }