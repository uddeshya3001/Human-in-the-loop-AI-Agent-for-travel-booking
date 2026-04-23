"""
Pydantic models for data validation and structure.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a single tool call with arguments."""
    name: str
    args: Dict[str, Any]


class FlightOption(BaseModel):
    """Flight search result."""
    airline: str
    route: str
    price_usd: int


class HotelOption(BaseModel):
    """Hotel search result."""
    name: str
    nightly_usd: int


class CarRentalOption(BaseModel):
    """Car rental search result."""
    company: str
    car_type: str
    daily_usd: int


class ActivityOption(BaseModel):
    """Activity/tour search result."""
    name: str
    category: str
    price_usd: int
    duration_hours: float


class TravelPlan(BaseModel):
    """Complete travel plan with all tool calls."""
    trip_title: str
    origin: str
    destination: str
    depart_date: str
    return_date: str
    budget_usd: int
    tool_calls: List[ToolCall]
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "trip_title": "Paris Adventure",
                "origin": "New York",
                "destination": "Paris",
                "depart_date": "2026-06-10",
                "return_date": "2026-06-15",
                "budget_usd": 3000,
                "tool_calls": []
            }
        }