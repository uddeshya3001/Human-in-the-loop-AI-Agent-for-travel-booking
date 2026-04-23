"""
Flight search tool - returns mock flight options.
"""

from config.settings import MAX_FLIGHT_OPTIONS


def tool_search_flights(origin, destination, depart_date, return_date, budget_usd):
    """
    Search for flights between origin and destination.
    
    Args:
        origin: Departure city
        destination: Arrival city
        depart_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD)
        budget_usd: Flight budget in USD
    
    Returns:
        Dictionary with tool name and flight results
    """
    options = [
        {
            "airline": "SkyJet",
            "route": f"{origin} → {destination}",
            "price_usd": int(budget_usd * 0.55),
            "departure": depart_date,
            "return": return_date,
            "stops": "Direct",
            "duration": "7h 30m"
        },
        {
            "airline": "AeroBlue",
            "route": f"{origin} → {destination}",
            "price_usd": int(budget_usd * 0.70),
            "departure": depart_date,
            "return": return_date,
            "stops": "1 Stop",
            "duration": "10h 15m"
        },
        {
            "airline": "Nimbus Air",
            "route": f"{origin} → {destination}",
            "price_usd": int(budget_usd * 0.62),
            "departure": depart_date,
            "return": return_date,
            "stops": "Direct",
            "duration": "7h 45m"
        },
    ]
    
    # Sort by price and return top options
    sorted_options = sorted(options, key=lambda x: x["price_usd"])[:MAX_FLIGHT_OPTIONS]
    
    return {
        "tool": "search_flights",
        "results": sorted_options
    }