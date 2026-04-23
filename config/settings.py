"""
Configuration and constants for the travel agent application.
"""

# LLM Settings
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.7

# Budget Settings
DEFAULT_BUDGET = 3000
MIN_BUDGET = 500
MAX_BUDGET = 50000

# Tool Settings
MAX_FLIGHT_OPTIONS = 3
MAX_HOTEL_OPTIONS = 3
MAX_CAR_OPTIONS = 3
MAX_ACTIVITY_OPTIONS = 4

# UI Settings
THEME_COLOR = "#FF4B4B"
SUCCESS_COLOR = "#00C853"
WARNING_COLOR = "#FFA726"
ERROR_COLOR = "#EF5350"

# Icons
ICONS = {
    "flight": "✈️",
    "hotel": "🏨",
    "car": "🚗",
    "activity": "🎭",
    "budget": "💰",
    "calendar": "📅",
    "location": "📍",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌"
}

# Date Format
DATE_FORMAT = "%Y-%m-%d"
DISPLAY_DATE_FORMAT = "%B %d, %Y"