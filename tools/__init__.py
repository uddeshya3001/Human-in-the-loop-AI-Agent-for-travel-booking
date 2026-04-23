"""
Tool registry - imports and exports all available tools.
"""

from .flights import tool_search_flights
from .hotels import tool_search_hotels
from .cars import tool_search_cars
from .activities import tool_search_activities


# Tool registry mapping tool names to functions
TOOLS = {
    "search_flights": tool_search_flights,
    "search_hotels": tool_search_hotels,
    "search_cars": tool_search_cars,
    "search_activities": tool_search_activities
}


__all__ = [
    "TOOLS",
    "tool_search_flights",
    "tool_search_hotels",
    "tool_search_cars",
    "tool_search_activities"
]